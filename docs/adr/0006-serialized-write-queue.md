# 0006. Serialized write queue

- Status: accepted
- Date: 2026-10-01

## Context

`Coordinator.async_write` wrote one field and then called
`async_request_refresh()`. A full poll is roughly 34 sequential block reads,
because [0002](0002-contiguous-only-register-blocks.md) forbids bridging a gap,
and the coordinator's default debouncer has `immediate=True`, so the first write
of a bundle fired that poll at once.

A consumer writing fifteen fields per cycle is not hypothetical. The
`schwoerer_climate_control` controller writes six room setpoints, six HVAC modes,
the fan level and two switches every time it decides something, and the device
grants one Modbus session at a time ([0001](0001-shared-modbus-units-and-device-model.md)).
The reads of the immediate poll therefore interleaved with the writes still going
out, and writes were silently discarded. That is the failure that made the 1.x
write path unusable.

Nothing in the integration serialized or paced its own writes either.
`message_spacing` is 0 and nothing sets it, so `modbus_connection`'s `Pacer`
takes a fast path that does not even take its lock. The only mutual exclusion is
`tmodbus`'s per-request lock, which makes one request atomic but lets a write
slot in between a poll's reads rather than waiting for it. Nothing checked that
a write had landed.

`docs/design.md` in `homeassistant-schwoerer-climate-control`, section
Schreibdisziplin, splits the protection across two layers and assigns transport
safety to this repo, because the connection lives here and every other writer
benefits too, the UI and hand-written scripts included. Intent discipline, which
is writing only diffs, bundling per decision, debouncing and rate-capping, stays
in the controller.

## Considered Options

- Keep write-then-refresh and raise the debouncer's cooldown.
- Pace the whole shared connection with `unit.set_message_spacing`.
- Route writes through a serialized queue that paces and verifies them itself.

## Decision

We will route every write through one worker task in `write_queue.py`.

- **Serialized.** A single worker, so two writes never overlap on the connection.
- **Paced.** `WRITE_SPACING` between every request the queue makes, readbacks
  included, measured from when the previous request finished, because the device
  needs time between register accesses whichever direction they go.
- **Coalesced per field, structurally.** The pending map holds at most one entry
  per field and a newer value replaces a still-queued one in place, releasing the
  superseded caller at once. There is deliberately no gathering timer: a caller
  awaits its write going out (see [0007](0007-write-calls-return-on-acknowledgement.md)),
  so a window would delay every write by its own length. `WRITE_SPACING` is what
  makes a queue form during a burst for coalescing to collapse.
- **Verified by reading back that one field.** One request against the field's
  own registers, never a poll. The comparison is against the words
  `field.encode` produces, not the decoded value, so a temperature stored in
  tenths of a degree needs no float tolerance to compare exactly.
- **One poll once the queue has drained,** instead of one per write.
- **The worker is a background task of the config entry,** so unloading cancels
  it rather than stranding it on a device that stopped answering. It starts on
  the next tick rather than eagerly, so a consumer that submits a bundle
  concurrently has all of it queued before the first write goes out and the whole
  bundle coalesces and drains in one pass.

Pacing covers the queue's own requests and not the shared connection. Spacing the
unit itself would slow the 34-block poll for every consumer on that connection,
which is a cost paid by everyone to protect against a burst only we create.

Tests pin the behaviour in `tests/test_write_queue.py`, in particular
`test_a_bundle_of_writes_polls_once` and
`test_no_poll_interleaves_with_the_burst`.

## Consequences

Fifteen fields now cost fifteen paced writes, fifteen single-register readbacks
and one poll, against fifteen writes racing two interleaved 34-read polls. A
write the device acknowledges and then discards is reported instead of
disappearing.

Writes are serialized, so they now queue behind each other. A UI action submitted
while a controller bundle is in the queue waits for it, which at the shipped
spacing is several seconds before the user's own write is even issued. Before, it
would have been issued immediately, interleaved. `WRITE_SPACING` is the dial, and
the cost is the point: that interleaving is what lost writes.

Coalescing means a superseded write reports success without reaching the wire.
That is the intent, and no current consumer writes one field twice concurrently,
but it is a contract a future one could be surprised by.

Verification assumes a register reads back what was written to it. A register the
firmware self-clears or normalises will report a mismatch on every write, and
only hardware can say which ones do; the shock ventilation trigger is the obvious
suspect. How many times a mismatch is re-written is a constant rather than a
decision recorded here, and it currently ships at 0 so that the first hardware
run observes without amplifying. `docs/todo.md` carries the follow-up.

A write can still be issued immediately after a poll's read, because the poll
does not go through the queue's pacing. Closing that would mean pacing the shared
unit, which is the option rejected above.

The queue is a module that imports nothing from Home Assistant beyond its logger,
so it is testable on its own, and the coordinator keeps only the wiring.
