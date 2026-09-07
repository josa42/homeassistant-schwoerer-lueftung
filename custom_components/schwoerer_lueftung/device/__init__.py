"""The Schwörer ventilation device, reached through a Modbus unit.

Follows the device-object pattern: takes a ``ModbusUnit``, exposes each
sub-system as an attribute, and reports per-poll what refreshed and what
failed. No Home Assistant imports, so it is testable against the mock backend
with no hardware and no Home Assistant in the loop.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from modbus_connection import (
    ModbusConnectionError,
    ModbusError,
    ModbusTimeoutError,
)
from modbus_connection.model import Component, ComponentGroup

from .components import (
    Alarms,
    GroundHeatExchanger,
    Heating,
    OperatingHours,
    Room,
    Temperatures,
    Ventilation,
)

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit

__all__ = [
    "SchwoererDevice",
    "UpdateReport",
]


@dataclass
class UpdateReport:
    """What one poll managed to refresh.

    Entities read their sub-system's name out of this to decide whether they
    are available, so a device that refuses one block does not take the rest
    of the entities down with it.
    """

    updated: list[str] = field(default_factory=list)
    failed: dict[str, ModbusError] = field(default_factory=dict)


class SchwoererDevice:
    """A Schwörer WGT or WRT ventilation unit.

    Which sub-systems exist is settled by the config entry rather than by
    probing: the user tells us the device type and whether there is a ground
    heat exchanger during setup. Absent sub-systems are simply never
    constructed, so their registers are never read.
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

        self.ventilation = Ventilation(unit)
        self.temperatures = Temperatures(unit)
        self.alarms = Alarms(unit)
        self.operating_hours = OperatingHours(unit)

        self.heating = Heating(unit) if has_heating else None
        self.ground_heat_exchanger = (
            GroundHeatExchanger(unit) if has_ground_heat_exchanger else None
        )

        # A room's fields are interleaved across the map, so each room is its
        # own component placed at its index. Grouping them lets the planner
        # pool the instances: N rooms still cost six block reads, not six per
        # room.
        self.rooms: dict[int, Room] = {n: Room(unit, index=n) for n in room_numbers}
        self._room_group = (
            ComponentGroup(unit, list(self.rooms.values())) if self.rooms else None
        )

        self._names = tuple(
            name
            for name in (
                "ventilation",
                "temperatures",
                "alarms",
                "operating_hours",
                "heating",
                "ground_heat_exchanger",
                "rooms",
            )
            if self._subsystem(name) is not None
        )

    def _subsystem(self, name: str) -> Component | ComponentGroup | None:
        """Return the pollable object behind a report name."""
        if name == "rooms":
            return self._room_group
        return getattr(self, name)

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
            subsystem = self._subsystem(name)
            assert subsystem is not None
            try:
                await subsystem.async_update(notify=False)
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
            subsystem = self._subsystem(name)
            assert subsystem is not None
            for space, values in (await subsystem.async_read_raw(notify=False)).items():
                raw.setdefault(space, {}).update(values)
        return raw
