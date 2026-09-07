"""Tests for the device layer — decoding, the read plan, and failure isolation.

These need no Home Assistant: the device object takes a ``ModbusUnit`` and the
mock backend is one.
"""

from __future__ import annotations

import pytest
from modbus_connection import IllegalDataAddressError
from modbus_connection.mock import MockModbusUnit

from custom_components.schwoerer_lueftung.device import SchwoererDevice
from custom_components.schwoerer_lueftung.device.components import (
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

# Registers that only exist on a device with the matching hardware. Nothing may
# read these unless the corresponding component was constructed.
HEATING_ONLY = {114, 115, 116, 201, 202, 203, 206, 207, 230, 231, 232, 233, 234}
GROUND_HEAT_EXCHANGER_ONLY = {121, 200, 813}


def addresses_read(unit: MockModbusUnit) -> set[int]:
    """Every register address the recorded block reads covered."""
    return {
        address
        for event in unit.read_events
        for address in range(event.address, event.address + event.count)
    }


def make_device(unit: MockModbusUnit, **kwargs) -> SchwoererDevice:
    options = {
        "has_heating": True,
        "has_ground_heat_exchanger": True,
        "room_numbers": [1, 2],
    }
    return SchwoererDevice(unit, **(options | kwargs))


async def test_decodes_the_register_map(unit: MockModbusUnit) -> None:
    """Values come back scaled and typed."""
    device = make_device(unit)
    await device.async_update()

    assert device.ventilation.current_fan_level == 3
    assert device.ventilation.linear_fan_power == 60
    assert device.temperatures.temperature_t5_exhaust_air == 21.5
    assert device.temperatures.temperature_t10_outdoor == 7.8
    assert device.alarms.device_filter_remaining == 45
    assert device.operating_hours.operating_hours_fan == 12000

    assert device.heating is not None
    assert device.heating.heat_pump_status == 5
    assert device.heating.temperature_t8_condenser == 42.0

    assert device.ground_heat_exchanger is not None
    assert (
        device.ground_heat_exchanger.temperature_t1_after_ground_heat_exchanger == 9.5
    )


async def test_room_fields_are_placed_per_room(unit: MockModbusUnit) -> None:
    """Room n reads base + (n - 1) for each field, not a block per room."""
    device = make_device(unit, room_numbers=[1, 2, 3])
    await device.async_update()

    # 360, 361, 362 were seeded 21.0, 21.1, 21.2.
    assert device.rooms[1].current_temperature == 21.0
    assert device.rooms[2].current_temperature == 21.1
    assert device.rooms[3].current_temperature == 21.2
    assert device.rooms[2].scheduled_heating_enabled == 1


async def test_rooms_are_pooled_into_six_reads(unit: MockModbusUnit) -> None:
    """A room costs no extra round trip: the group pools the instances."""
    device = make_device(unit, room_numbers=list(range(1, 18)))
    await device.async_update()

    room_reads = [e for e in unit.read_events if 360 <= e.address <= 516]
    assert len(room_reads) == 6
    assert all(event.count == 17 for event in room_reads)


async def test_a_wrt_never_reads_optional_hardware(unit: MockModbusUnit) -> None:
    """The whole point of the split: those addresses are never asked for."""
    device = make_device(
        unit, has_heating=False, has_ground_heat_exchanger=False, room_numbers=[]
    )
    await device.async_update()

    read = addresses_read(unit)
    assert not read & HEATING_ONLY
    assert not read & GROUND_HEAT_EXCHANGER_ONLY


async def test_a_wgt_does_read_optional_hardware(unit: MockModbusUnit) -> None:
    """The carve-outs must not leave the registers unread when they do exist."""
    device = make_device(unit)
    await device.async_update()

    read = addresses_read(unit)
    assert {114, 116, 201, 230, 234} <= read
    assert GROUND_HEAT_EXCHANGER_ONLY <= read


def declared_addresses() -> set[int]:
    """Every address any component declares a field at, all 17 rooms included."""
    addresses: set[int] = set()
    for component in (
        Ventilation,
        Temperatures,
        Alarms,
        OperatingHours,
        Heating,
        GroundHeatExchanger,
        UndocumentedTemperatures,
        Clock,
    ):
        addresses |= {
            field.address
            for field in vars(component).values()
            if hasattr(field, "address")
        }
    for base in (360, 400, 420, 440, 460, 500):
        addresses |= set(range(base, base + 17))
    return addresses


async def test_every_address_read_has_a_field_behind_it(unit: MockModbusUnit) -> None:
    """The firmware refuses any block containing an address it does not implement.

    A real WGT answered exception code 2 to holding 100-112 — one block over
    the fields at 100-104 and 110-112, bridging the unimplemented 105-109. So
    a block may never cover an address we did not declare a field for.
    """
    device = make_device(unit, room_numbers=list(range(1, 18)))
    await device.async_update()

    assert not addresses_read(unit) - declared_addresses()


async def test_reads_never_bridge_a_gap(unit: MockModbusUnit) -> None:
    """The exact block the device rejected must not be formed again."""
    device = make_device(unit)
    await device.async_update()

    blocks = {(event.address, event.count) for event in unit.read_events}

    # 100-112 was the failing read: it spans the unimplemented 105-109.
    assert (100, 13) not in blocks
    # The two runs either side of that gap are read separately instead.
    assert (100, 5) in blocks
    assert (110, 3) in blocks
    # 240 and 242-248 likewise, with 241 unimplemented between them.
    assert (240, 1) in blocks
    assert (242, 7) in blocks


async def test_a_refused_subsystem_fails_alone(unit: MockModbusUnit) -> None:
    """A device that rejects the heat pump registers keeps the rest polling."""
    for address in (114, 115, 116):
        unit.fail_read(address, IllegalDataAddressError(2))

    device = make_device(unit)
    report = await device.async_update()

    assert "heating" in report.failed
    assert isinstance(report.failed["heating"], IllegalDataAddressError)
    assert "ventilation" in report.updated
    assert "rooms" in report.updated
    assert device.ventilation.current_fan_level == 3
    assert device.rooms[2].current_temperature == 21.1


async def test_writes_use_fc16(unit: MockModbusUnit) -> None:
    """The device rejects FC06, so even a single register goes out as FC16."""
    written = []
    unit.on_write(written.append)

    ventilation = Ventilation(unit)
    await ventilation.async_update()
    await ventilation.write("shock_ventilation", 1)

    assert len(written) == 1
    event = written[0]
    assert event.address == 111
    assert event.values == [1]
    # 0x10 is Write Multiple Registers; 0x06 would be the single-register form
    # this device rejects.
    assert event.function_code == 0x10
    assert unit.holding[111] == 1


async def test_room_writes_land_on_the_rooms_address(unit: MockModbusUnit) -> None:
    room = Room(unit, index=3)
    await room.async_update()
    await room.write("target_temperature", 21.5)

    assert unit.holding[402] == 215


@pytest.mark.parametrize("value", [9.9, 30.1])
async def test_room_setpoint_is_range_checked(
    unit: MockModbusUnit, value: float
) -> None:
    """The validator stops an out-of-range setpoint before it reaches the wire."""
    room = Room(unit, index=1)
    await room.async_update()

    with pytest.raises(ValueError):
        await room.write("target_temperature", value)


async def test_read_raw_covers_every_subsystem(unit: MockModbusUnit) -> None:
    """Diagnostics returns the raw words, undecoded, keyed by address."""
    device = make_device(unit)
    raw = await device.async_read_raw()

    assert raw["holding"][204] == 215  # raw, not 21.5
    assert raw["holding"][114] == 5
    assert raw["holding"][360] == 210


async def test_undocumented_t9_decodes_as_a_temperature(unit: MockModbusUnit) -> None:
    """208 is absent from the datasheet, which numbers T1-T8 and T10."""
    device = make_device(unit)
    await device.async_update()

    assert device.undocumented_temperatures.temperature_t9 == 25.9


async def test_device_clock_reads_as_a_datetime(unit: MockModbusUnit) -> None:
    """620-625 is year, month, day, hour, minute, second."""
    from datetime import datetime

    device = make_device(unit)
    await device.async_update()

    assert device.clock.datetime == datetime(2026, 9, 7, 12, 21, 32)


async def test_device_clock_folds_nonsense_into_none(unit: MockModbusUnit) -> None:
    """A unit with a dead clock must not raise out of the poll."""
    unit.holding[621] = 13  # month 13
    device = make_device(unit)
    await device.async_update()

    assert device.clock.datetime is None


async def test_undocumented_registers_fail_alone(unit: MockModbusUnit) -> None:
    """A firmware without them must not lose the documented sensors."""
    unit.fail_read(208, IllegalDataAddressError(2))
    for address in range(620, 626):
        unit.fail_read(address, IllegalDataAddressError(2))

    device = make_device(unit)
    report = await device.async_update()

    assert set(report.failed) == {"undocumented_temperatures", "clock"}
    assert "temperatures" in report.updated
    assert device.temperatures.temperature_t10_outdoor == 7.8
