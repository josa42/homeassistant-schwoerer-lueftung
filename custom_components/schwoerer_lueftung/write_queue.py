"""Serialize, pace and verify writes to the device.

Writing used to mean writing one field and then asking for a full poll, so a
consumer setting fifteen fields paid fifteen polls of roughly thirty-four block
reads each, over the one Modbus session the device grants. Those reads
interleaved with the remaining writes and some of the writes were silently
discarded, which is the failure this queue exists to remove.

Everything here is one worker task writing one field at a time:

- Writes are serialized, so two never overlap on the connection.
- A gap of :data:`WRITE_SPACING` separates every request, reads included,
  because the device needs time between register accesses.
- Only the newest value per field survives. A write still waiting in the queue
  is replaced rather than sent, so three moves of one slider cost one write.
- Each write is read back and re-sent while the device disagrees. Comparing the
  register words rather than the decoded values keeps the check exact.
- One poll follows the whole burst, once the queue has drained, instead of one
  poll per write.

:meth:`WriteQueue.async_write` returns as soon as the request has been
acknowledged, not once it has been verified. That keeps the errors a caller can
act on - an unreachable device, a value its field rejects - on the caller's own
await, while the readback, the retries and the poll run behind it. A write the
device acknowledges and then discards is therefore logged and re-sent rather
than raised.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable, Coroutine
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from modbus_connection.model import PackedBitsField, RegisterField

from .const import WRITE_READBACK_DELAY, WRITE_READBACK_RETRIES, WRITE_SPACING

if TYPE_CHECKING:
    from modbus_connection.model import Component, ResolvedField

_LOGGER = logging.getLogger(__name__)

type _Key = tuple[Component, str]
"""A field on one sub-system: what writes are coalesced by."""


@dataclass
class _Pending:
    """One queued write, and the caller waiting for it to go out."""

    component: Component
    field: str
    value: Any
    issued: asyncio.Future[None]


def _settle(future: asyncio.Future[None], error: BaseException | None = None) -> None:
    """Release the caller waiting on ``future``, if anything still is.

    A caller that gave up has already cancelled its future, so every resolution
    goes through here rather than assuming the future is still pending.
    """
    if future.done():
        return
    if error is None:
        future.set_result(None)
    else:
        future.set_exception(error)


class WriteQueue:
    """Write queued fields in order, with a gap and a readback for each."""

    def __init__(
        self,
        spawn: Callable[[Coroutine[Any, Any, None]], object],
        refresh: Callable[[], Awaitable[None]],
    ) -> None:
        """Take how to start the worker, and what to do once it idles.

        ``spawn`` ties the worker to a lifecycle that cancels it; the config
        entry's background tasks do that, so unloading cannot strand the queue
        waiting on a device that stopped answering.
        """
        self._spawn = spawn
        self._refresh = refresh

        # Ordered by insertion and indexed by field at the same time: the first
        # entry is the next write, and a second write to a field already in
        # here replaces it in place rather than queueing behind it.
        self._pending: dict[_Key, _Pending] = {}

        self._wake = asyncio.Event()
        self._idle = asyncio.Event()
        self._idle.set()

        self._worker: object | None = None
        self._last_request_at = 0.0

    async def async_write(self, component: Component, field: str, value: Any) -> None:
        """Queue a write and wait until the device has acknowledged it.

        Raises whatever the write raises: ``ModbusError`` if the device cannot
        be reached, ``ValueError`` if the field rejects the value, and
        ``AttributeError`` if the field is unknown or read-only.
        """
        key = (component, field)
        pending = _Pending(
            component, field, value, asyncio.get_running_loop().create_future()
        )

        # Replacing the entry keeps the place the field already held in the
        # queue, and the caller whose value this supersedes is released now:
        # the value it asked for is obsolete, so there is nothing left to wait
        # for. Forgetting to release it is how coalescing hangs a caller.
        superseded = self._pending.get(key)
        self._pending[key] = pending
        if superseded is not None:
            _settle(superseded.issued)

        self._idle.clear()
        self._wake.set()
        self._ensure_worker()

        await pending.issued

    async def async_join(self) -> None:
        """Wait until the queue has drained and its poll has been asked for.

        Home Assistant deliberately does not wait for background tasks in
        ``async_block_till_done``, so anything that needs the queue finished -
        a test, mainly - asks here.
        """
        await self._idle.wait()

    def _ensure_worker(self) -> None:
        if self._worker is None:
            self._worker = self._spawn(self._run())

    async def _run(self) -> None:
        """Drain the queue, then poll once, for as long as work arrives."""
        try:
            while True:
                await self._wake.wait()

                while self._pending:
                    key, item = next(iter(self._pending.items()))
                    del self._pending[key]
                    await self._write(key, item)

                self._wake.clear()
                await self._drain_refresh()

                # A write that arrived during the poll has already cleared the
                # flag and will be picked up by the next pass.
                if not self._pending:
                    self._idle.set()
        finally:
            # Whether this was cancelled on unload or died of something
            # unexpected, nobody may be left waiting on a worker that has
            # stopped, and the next write has to be able to start a new one.
            self._worker = None
            for item in self._pending.values():
                item.issued.cancel()
            self._pending.clear()
            self._idle.set()

    async def _write(self, key: _Key, item: _Pending) -> None:
        """Write one field and verify it. Never raises except on cancellation."""
        try:
            await self._paced(item.component.write(item.field, item.value))
        except asyncio.CancelledError:
            item.issued.cancel()
            raise
        except Exception as err:
            # Deliberately broad: whatever the write raises is the caller's to
            # interpret, and handing it back unchanged is what keeps the error
            # contract the same as writing the field directly.
            _settle(item.issued, err)
            return

        # The caller is free from here on, so a failure past this point is ours
        # to log rather than to hand back.
        _settle(item.issued)

        try:
            await self._verify(key, item)
        except asyncio.CancelledError:
            raise
        except Exception:
            _LOGGER.exception("Failed to verify the write of %s", item.field)

    async def _verify(self, key: _Key, item: _Pending) -> None:
        """Read the field back, and write it again while the device disagrees."""
        resolved = item.component.resolved_fields.get(item.field)
        if resolved is None:
            return

        expected = self._expected_words(item, resolved)
        if expected is None:
            _LOGGER.debug("No readback for %s; leaving it to the poll", item.field)
            return

        for attempt in range(WRITE_READBACK_RETRIES + 1):
            if WRITE_READBACK_DELAY:
                await asyncio.sleep(WRITE_READBACK_DELAY)

            if self._superseded(key):
                return

            actual = await self._read_back(item, resolved)
            if actual == expected:
                return

            if attempt == WRITE_READBACK_RETRIES:
                _LOGGER.error(
                    "Wrote %s to %s at register %s, but the device still reads "
                    "%s instead of %s after %s attempts",
                    item.value,
                    item.field,
                    resolved.address,
                    actual,
                    expected,
                    attempt + 1,
                )
                return

            # Checked again: the readback above awaited, and a newer value for
            # this field may have arrived while it did. Re-sending the stale
            # value on top of it would put the wrong number on the device until
            # the queue caught up.
            if self._superseded(key):
                return

            await self._paced(item.component.write(item.field, item.value))

    def _superseded(self, key: _Key) -> bool:
        """Whether a newer value for this field is already queued.

        Retrying a write that something has already replaced would only fight
        the newer value, so verification gives up instead.
        """
        return key in self._pending

    def _expected_words(
        self, item: _Pending, resolved: ResolvedField
    ) -> list[int] | list[bool] | None:
        """The words the device should hold, or None if we cannot say.

        Comparing encoded words rather than decoded values keeps the check
        exact: a temperature is a tenth of a degree on the wire, so a decoded
        comparison would need a float tolerance and this does not.
        """
        field = resolved.field
        value = item.value

        # The validator is what decides the value actually written, so the
        # comparison has to run it too, exactly as the library does.
        if callable(field.writable):
            value = field.writable(value)

        if not isinstance(field, RegisterField):
            return [bool(value)]

        if resolved.space != "holding":
            return None
        if isinstance(field, PackedBitsField) or field.scale_register is not None:
            # Both need a register read to encode against, so what the device
            # should be holding is not ours to predict.
            return None

        return field.encode(value)

    async def _read_back(
        self, item: _Pending, resolved: ResolvedField
    ) -> list[int] | list[bool]:
        """Read just this field, which is one request rather than a poll."""
        unit = item.component.modbus_unit
        if resolved.space == "holding":
            return await self._paced(
                unit.read_holding_registers(resolved.address, resolved.count)
            )
        return await self._paced(unit.read_coils(resolved.address, 1))

    async def _drain_refresh(self) -> None:
        """Poll once for the whole burst that just drained."""
        try:
            await self._refresh()
        except asyncio.CancelledError:
            raise
        except Exception:
            _LOGGER.exception("Failed to refresh after writing")

    async def _paced[T](self, request: Awaitable[T]) -> T:
        """Run one request, no sooner than ``WRITE_SPACING`` after the last.

        The gap is measured from when the previous request finished, and every
        request goes through here, readbacks included: the device needs the
        time between register accesses whichever direction they go.
        """
        wait = WRITE_SPACING - (time.monotonic() - self._last_request_at)
        if wait > 0:
            await asyncio.sleep(wait)
        try:
            return await request
        finally:
            self._last_request_at = time.monotonic()
