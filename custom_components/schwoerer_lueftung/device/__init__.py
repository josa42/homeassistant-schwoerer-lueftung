"""The Schwörer ventilation device, reached through a Modbus unit.

Follows the device-object pattern: takes a ``ModbusUnit``, exposes each
sub-system as an attribute, and reports per-poll what refreshed and what
failed. No Home Assistant imports, so it is testable against the mock backend
with no hardware and no Home Assistant in the loop.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from modbus_connection import (
    IllegalDataAddressError,
    ModbusConnectionError,
    ModbusError,
    ModbusTimeoutError,
)
from modbus_connection.model import Component, ComponentGroup

from .components import (
    Alarms,
    Clock,
    GroundHeatExchanger,
    Heating,
    OperatingHours,
    Room,
    Temperatures,
    UndocumentedTemperatures,
    Ventilation,
)

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit

__all__ = [
    "SchwoererDevice",
    "UnservedField",
    "UpdateReport",
]

_LOGGER = logging.getLogger(__name__)

type Raw = dict[str, dict[int, int | bool]]


@dataclass
class UpdateReport:
    """What one poll managed to refresh.

    Entities read their sub-system's name out of this to decide whether they
    are available, so a device that refuses one block does not take the rest
    of the entities down with it.
    """

    updated: list[str] = field(default_factory=list)
    failed: dict[str, ModbusError] = field(default_factory=dict)


@dataclass(frozen=True)
class UnservedField:
    """A field dropped because the device refused its address."""

    subsystem: str
    field: str
    address: int
    room: int | None = None


class SchwoererDevice:
    """A Schwörer WGT or WRT ventilation unit.

    Which sub-systems exist is settled by the config entry rather than by
    probing: the user tells us the device type and whether there is a ground
    heat exchanger during setup. Absent sub-systems are simply never
    constructed, so their registers are never read.

    Which registers a present sub-system serves does vary by firmware, and that
    is probed: a field the device refuses is dropped on the first read that
    hits it and listed in ``unserved``. The list lives as long as the device
    object, so a firmware update shows up on the next reload.
    """

    def __init__(
        self,
        unit: ModbusUnit,
        *,
        has_heating: bool,
        has_ground_heat_exchanger: bool,
        room_numbers: list[int],
    ) -> None:
        self._unit = unit
        self.unserved: list[UnservedField] = []

        self.ventilation = Ventilation(unit)
        self.temperatures = Temperatures(unit)
        self.alarms = Alarms(unit)
        self.operating_hours = OperatingHours(unit)

        # Undocumented, found by probing one unit. Always constructed, since
        # neither depends on installed hardware, but kept apart so a firmware
        # without them fails only its own sub-system.
        self.undocumented_temperatures = UndocumentedTemperatures(unit)
        self.clock = Clock(unit)

        self.heating = Heating(unit) if has_heating else None
        self.ground_heat_exchanger = (
            GroundHeatExchanger(unit) if has_ground_heat_exchanger else None
        )

        # A room's fields are interleaved across the map, so each room is its
        # own component placed at its index. Grouping them lets the planner
        # pool the instances: N rooms still cost six block reads, not six per
        # room.
        self.rooms: dict[int, Room] = {n: Room(unit, index=n) for n in room_numbers}
        if not has_heating:
            # Without heating a room has nothing to set, so only its
            # temperature is surfaced. The setpoint and heating registers are
            # not read at all.
            for room in self.rooms.values():
                room.restrict_fields(["current_temperature"])
        self._room_group = (
            ComponentGroup(unit, list(self.rooms.values())) if self.rooms else None
        )

        self._names = tuple(
            name
            for name in (
                "ventilation",
                "temperatures",
                "undocumented_temperatures",
                "alarms",
                "operating_hours",
                "heating",
                "ground_heat_exchanger",
                "clock",
                "rooms",
            )
            if self._subsystem(name) is not None
        )

    def _subsystem(self, name: str) -> Component | ComponentGroup | None:
        """Return the pollable object behind a report name."""
        if name == "rooms":
            return self._room_group
        return getattr(self, name)

    def _components(self, name: str) -> list[tuple[int | None, Component]]:
        """The components behind a report name, each with its room number."""
        if name == "rooms":
            return list(self.rooms.items())
        component = getattr(self, name)
        return [] if component is None else [(None, component)]

    async def _async_update_subsystem(self, name: str, *, raw: bool) -> Raw:
        """Read one sub-system, dropping fields at addresses the device lacks.

        Firmware versions differ in which registers they implement, and the
        device refuses a whole block for one address it does not have. On such
        a refusal the fields in that block are probed one by one, the refused
        ones are dropped, and the read is tried again. Each pass drops at least
        one field, so this ends.
        """
        subsystem = self._subsystem(name)
        assert subsystem is not None
        while True:
            try:
                if raw:
                    return await subsystem.async_read_raw(notify=False)
                await subsystem.async_update(notify=False)
                return {}
            except IllegalDataAddressError as err:
                if not await self._async_drop_unserved(name, err):
                    raise

    async def _async_drop_unserved(
        self, name: str, err: IllegalDataAddressError
    ) -> bool:
        """Drop the fields in the refused block the device does not serve.

        Only Illegal Data Address counts as proof that a register is missing.
        Any other error while probing propagates, so a timeout or a dropped
        link never costs a field. Returns False when every field in the block
        reads on its own, which leaves the refusal unexplained.
        """
        block = err.block
        if block is None or block.space != "holding":
            return False
        end = block.address + block.count

        dropped = False
        for room, component in self._components(name):
            refused: list[UnservedField] = []
            for field_name, resolved in component.resolved_fields.items():
                if not block.address <= resolved.address < end:
                    continue
                try:
                    await self._unit.read_holding_registers(
                        resolved.address, resolved.count
                    )
                except IllegalDataAddressError:
                    refused.append(
                        UnservedField(name, field_name, resolved.address, room)
                    )
            if not refused:
                continue
            for unserved in refused:
                _LOGGER.info(
                    "The device does not serve register %s (%s), skipping it",
                    unserved.address,
                    unserved.field,
                )
            names = {unserved.field for unserved in refused}
            component.restrict_fields(
                [f for f in component.resolved_fields if f not in names]
            )
            self.unserved.extend(refused)
            dropped = True
        return dropped

    @property
    def unit(self) -> ModbusUnit:
        """The unit this device is read over."""
        return self._unit

    def room(self, number: int) -> Room | None:
        """Return the component for a configured room, if there is one."""
        return self.rooms.get(number)

    async def async_update(self) -> UpdateReport:
        """Refresh every sub-system, reporting which ones answered."""
        report = UpdateReport()
        for name in self._names:
            try:
                await self._async_update_subsystem(name, raw=False)
            except ModbusConnectionError:
                # The link is down; polling on would only wait for timeouts.
                raise
            except ModbusTimeoutError as err:
                if not report.updated and not report.failed:
                    # Nothing has answered yet, so assume the rest time out too.
                    raise
                report.failed[name] = err
            except ModbusError as err:
                report.failed[name] = err
            else:
                report.updated.append(name)

        for name in report.updated:
            subsystem = self._subsystem(name)
            assert subsystem is not None
            subsystem.notify()

        return report

    async def async_read_raw(self) -> dict[str, dict[int, int | bool]]:
        """Every register this device reads, undecoded — for diagnostics.

        Reads the device fresh, so it reflects the live register state at
        download time. A dump captured this way replays into the mock backend
        with ``load_raw()``, which is how a register map from a configuration
        we cannot test becomes a regression test.
        """
        raw: dict[str, dict[int, int | bool]] = {}
        for name in self._names:
            try:
                read = await self._async_update_subsystem(name, raw=True)
            except ModbusError:
                # A dump is most wanted precisely when something is refusing to
                # answer, so a failing sub-system must not cost us the rest.
                continue
            for space, values in read.items():
                raw.setdefault(space, {}).update(values)
        return raw
