"""Tests for the serialized, paced, verified write path.

The fault these pin down is the one that made 1.x unusable: a write followed by
a full device poll, so a consumer setting fifteen fields paid fifteen polls over
the one connection the device grants and its own writes were lost in the reads.
"""

from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from modbus_connection import ModbusConnectionError
from modbus_connection.mock import MockModbusUnit, WriteEvent
from pytest_homeassistant_custom_component.common import MockConfigEntry

# The ventilation component's first block, as the read planner shapes it. One
# read of exactly this block is one poll, which counts polls without counting
# all 34 blocks of one. A readback of a single register inside it is not a poll,
# so the count has to match, not overlap.
POLL_BLOCK = (100, 5)

OPERATION_MODE = 100
FAN_SPEED = 101
SHOCK_VENTILATION = 111


@pytest.fixture
def retrying():
    """Turn the readback retries on.

    They ship off, because re-writing assumes every writable register echoes
    what was written to it and the hardware has not shown that yet. The tests
    that cover retrying therefore ask for it instead of depending on the
    shipped default.
    """
    with patch(
        "custom_components.schwoerer_lueftung.write_queue.WRITE_READBACK_RETRIES", 2
    ):
        yield


async def setup_entry(hass: HomeAssistant, entry: MockConfigEntry) -> MockConfigEntry:
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def polls(unit: MockModbusUnit) -> int:
    """How many full device polls the unit has been asked for."""
    return sum(
        1
        for event in unit.read_events
        if event.register_type == "holding"
        and (event.address, event.count) == POLL_BLOCK
    )


def writes(unit: MockModbusUnit) -> list[WriteEvent]:
    """Record every write as it happens."""
    recorded: list[WriteEvent] = []
    unit.on_write(recorded.append)
    return recorded


# -- no poll per write --------------------------------------------------------


async def test_a_bundle_of_writes_polls_once(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
    instant_writes: None,
) -> None:
    """Fifteen fields cost one poll, not one poll each.

    This is the regression the queue exists for: the controller writes six
    setpoints, six modes, the fan level and two switches per cycle.
    """
    await setup_entry(hass, wgt_entry)
    coordinator = wgt_entry.runtime_data
    device = coordinator.device
    unit.read_events.clear()

    bundle = [
        (device.room(1), "target_temperature", 21.5),
        (device.room(2), "target_temperature", 22.0),
        (device.room(1), "base_temperature", 20.5),
        (device.room(2), "base_temperature", 20.0),
        (device.room(1), "auxiliary_heating_enabled", 1),
        (device.room(2), "auxiliary_heating_enabled", 0),
        (device.room(1), "scheduled_heating_enabled", 0),
        (device.room(2), "scheduled_heating_enabled", 1),
        (device.ventilation, "fan_speed", 3),
        (device.ventilation, "operation_mode", 1),
        (device.ventilation, "linear_fan_power", 55),
        (device.ventilation, "shock_ventilation", 1),
        (device.heating, "heating_cooling_function", 1),
        (device.heating, "heat_pump_heating_enabled", 1),
        (device.heating, "auxiliary_heating_enabled", 0),
    ]
    assert len(bundle) == 15

    await asyncio.gather(
        *(coordinator.async_write(*write) for write in bundle)
    )
    await coordinator.async_wait_for_writes()
    await hass.async_block_till_done()

    assert polls(unit) == 1

    # And every value actually landed.
    assert unit.holding[FAN_SPEED] == 3
    assert unit.holding[401] == 220  # room 2's setpoint, 22.0 in tenths
    assert unit.holding[SHOCK_VENTILATION] == 1


async def test_no_poll_interleaves_with_the_burst(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
    instant_writes: None,
) -> None:
    """The poll comes after the burst, not between its writes.

    Interleaving is the half of the old behaviour that actually lost writes:
    each write dragged a 34-block read behind it, over the one session the
    device grants, while the rest of the bundle was still going out.
    """
    await setup_entry(hass, wgt_entry)
    coordinator = wgt_entry.runtime_data
    ventilation = coordinator.device.ventilation
    unit.read_events.clear()

    # How many polls had happened by the time each write went out.
    polls_seen: list[int] = []
    unit.on_write(lambda event: polls_seen.append(polls(unit)))

    await asyncio.gather(
        coordinator.async_write(ventilation, "fan_speed", 3),
        coordinator.async_write(ventilation, "operation_mode", 1),
        coordinator.async_write(ventilation, "shock_ventilation", 1),
    )
    await coordinator.async_wait_for_writes()
    await hass.async_block_till_done()

    assert polls_seen == [0, 0, 0]
    assert polls(unit) == 1


# -- serializing and pacing ---------------------------------------------------


async def test_writes_reach_the_wire_one_at_a_time_in_order(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
    instant_writes: None,
) -> None:
    await setup_entry(hass, wgt_entry)
    coordinator = wgt_entry.runtime_data
    ventilation = coordinator.device.ventilation
    recorded = writes(unit)

    await asyncio.gather(
        coordinator.async_write(ventilation, "fan_speed", 3),
        coordinator.async_write(ventilation, "operation_mode", 1),
        coordinator.async_write(ventilation, "shock_ventilation", 1),
    )
    await coordinator.async_wait_for_writes()

    assert [event.address for event in recorded] == [
        FAN_SPEED,
        OPERATION_MODE,
        SHOCK_VENTILATION,
    ]


async def test_writes_are_paced(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
) -> None:
    """Every request waits out the gap the device needs.

    Asserting on the sleeps rather than on wall-clock deltas keeps this from
    going flaky on a loaded machine.
    """
    await setup_entry(hass, wgt_entry)
    coordinator = wgt_entry.runtime_data
    ventilation = coordinator.device.ventilation

    slept: list[float] = []
    real_sleep = asyncio.sleep

    async def record(delay: float, *args, **kwargs):
        slept.append(delay)
        return await real_sleep(0, *args, **kwargs)

    with (
        patch("custom_components.schwoerer_lueftung.write_queue.WRITE_SPACING", 0.2),
        patch(
            "custom_components.schwoerer_lueftung.write_queue.WRITE_READBACK_DELAY",
            0.1,
        ),
        patch(
            "custom_components.schwoerer_lueftung.write_queue.asyncio.sleep", record
        ),
    ):
        await asyncio.gather(
            coordinator.async_write(ventilation, "fan_speed", 3),
            coordinator.async_write(ventilation, "operation_mode", 1),
        )
        await coordinator.async_wait_for_writes()

    # Two writes and two readbacks, each readback preceded by its settle time
    # and every request by whatever is left of the spacing.
    assert slept.count(0.1) == 2
    assert any(0 < delay <= 0.2 for delay in slept)


# -- coalescing ---------------------------------------------------------------


async def test_three_writes_to_one_field_write_once(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
    instant_writes: None,
) -> None:
    """Only the newest value of a field is interesting, and nobody hangs."""
    await setup_entry(hass, wgt_entry)
    coordinator = wgt_entry.runtime_data
    ventilation = coordinator.device.ventilation
    recorded = writes(unit)

    # All three awaits have to return. A superseded write whose caller is never
    # released is how coalescing deadlocks, so the gather is the assertion.
    async with asyncio.timeout(5):
        await asyncio.gather(
            coordinator.async_write(ventilation, "fan_speed", 1),
            coordinator.async_write(ventilation, "fan_speed", 2),
            coordinator.async_write(ventilation, "fan_speed", 3),
        )
    await coordinator.async_wait_for_writes()

    assert [event.values for event in recorded] == [[3]]
    assert unit.holding[FAN_SPEED] == 3


async def test_writes_to_different_fields_are_not_coalesced(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
    instant_writes: None,
) -> None:
    """Coalescing is per field, so the same value in two rooms is two writes."""
    await setup_entry(hass, wgt_entry)
    coordinator = wgt_entry.runtime_data
    device = coordinator.device
    recorded = writes(unit)

    await asyncio.gather(
        coordinator.async_write(device.room(1), "target_temperature", 21.5),
        coordinator.async_write(device.room(2), "target_temperature", 21.5),
    )
    await coordinator.async_wait_for_writes()

    assert sorted(event.address for event in recorded) == [400, 401]


# -- readback and retry -------------------------------------------------------


async def test_a_confirmed_write_is_written_once_and_read_once(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
    instant_writes: None,
) -> None:
    """The readback is one register, not a poll, and there is no retry."""
    await setup_entry(hass, wgt_entry)
    coordinator = wgt_entry.runtime_data
    recorded = writes(unit)
    unit.read_events.clear()

    await coordinator.async_write(coordinator.device.ventilation, "fan_speed", 3)
    await coordinator.async_wait_for_writes()

    assert len(recorded) == 1

    # Exactly one single-register read of 101 before the drain poll reaches 100.
    readbacks = [
        event
        for event in unit.read_events
        if event.address == FAN_SPEED and event.count == 1
    ]
    assert len(readbacks) == 1


async def test_a_swallowed_write_is_retried_then_reported(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
    instant_writes: None,
    retrying: None,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A write the device acknowledges and discards is the 1.x failure.

    The mock stores a plain value on write, so a callback that puts the old one
    back models a device that accepts the request and ignores it.
    """
    await setup_entry(hass, wgt_entry)
    coordinator = wgt_entry.runtime_data
    original = unit.holding[FAN_SPEED]

    recorded = writes(unit)

    def swallow(event: WriteEvent) -> None:
        if event.address == FAN_SPEED:
            unit.holding[FAN_SPEED] = original

    unit.on_write(swallow)

    await coordinator.async_write(coordinator.device.ventilation, "fan_speed", 3)
    await coordinator.async_wait_for_writes()

    # One attempt plus WRITE_READBACK_RETRIES re-writes.
    assert [event.address for event in recorded] == [FAN_SPEED] * 3
    assert "but the device still reads" in caplog.text


async def test_a_write_that_lands_on_the_retry_stops_there(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
    instant_writes: None,
    retrying: None,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Retrying is what makes a flaky register land, so it stops when it does."""
    await setup_entry(hass, wgt_entry)
    coordinator = wgt_entry.runtime_data
    original = unit.holding[FAN_SPEED]

    recorded = writes(unit)

    def swallow_the_first(event: WriteEvent) -> None:
        if event.address == FAN_SPEED and len(recorded) == 1:
            unit.holding[FAN_SPEED] = original

    unit.on_write(swallow_the_first)

    await coordinator.async_write(coordinator.device.ventilation, "fan_speed", 3)
    await coordinator.async_wait_for_writes()

    assert [event.address for event in recorded] == [FAN_SPEED] * 2
    assert "but the device still reads" not in caplog.text
    assert unit.holding[FAN_SPEED] == 3


async def test_a_superseded_write_is_not_retried(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
    retrying: None,
) -> None:
    """A retry must not fight a newer value for the same field.

    The settle time before a readback is left real here, so the newer write is
    definitely queued by the time the older one checks whether to retry.
    """
    await setup_entry(hass, wgt_entry)
    coordinator = wgt_entry.runtime_data
    ventilation = coordinator.device.ventilation
    original = unit.holding[FAN_SPEED]

    recorded = writes(unit)

    def swallow_the_first(event: WriteEvent) -> None:
        if event.address == FAN_SPEED and len(recorded) == 1:
            unit.holding[FAN_SPEED] = original
            # A newer value arrives while the first one is being verified.
            hass.async_create_task(
                coordinator.async_write(ventilation, "fan_speed", 4)
            )

    unit.on_write(swallow_the_first)

    with (
        patch("custom_components.schwoerer_lueftung.write_queue.WRITE_SPACING", 0),
        patch(
            "custom_components.schwoerer_lueftung.write_queue.WRITE_READBACK_DELAY",
            0.05,
        ),
    ):
        await coordinator.async_write(ventilation, "fan_speed", 3)
        await coordinator.async_wait_for_writes()
        await hass.async_block_till_done()
        await coordinator.async_wait_for_writes()

    assert unit.holding[FAN_SPEED] == 4
    # The abandoned first write never re-sent its 3 on top of the 4.
    assert [event.values for event in recorded] == [[3], [4]]


# -- the error contract the callers rely on -----------------------------------


async def test_an_unreachable_device_still_raises(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
    instant_writes: None,
) -> None:
    """A write a consumer can act on still fails on the consumer's own await."""
    await setup_entry(hass, wgt_entry)
    coordinator = wgt_entry.runtime_data

    unit.fail_write(FAN_SPEED, ModbusConnectionError("connection reset"))

    with pytest.raises(UpdateFailed):
        await coordinator.async_write(coordinator.device.ventilation, "fan_speed", 3)


async def test_an_out_of_range_value_still_raises(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
    instant_writes: None,
) -> None:
    """The field's own validator rejects before anything reaches the wire."""
    await setup_entry(hass, wgt_entry)
    coordinator = wgt_entry.runtime_data
    recorded = writes(unit)

    with pytest.raises(ValueError, match="outside the accepted range"):
        await coordinator.async_write(
            coordinator.device.ventilation, "linear_fan_power", 200
        )

    assert recorded == []


async def test_an_unknown_field_still_raises(
    hass: HomeAssistant,
    mock_modbus,
    wgt_entry: MockConfigEntry,
    instant_writes: None,
) -> None:
    await setup_entry(hass, wgt_entry)
    coordinator = wgt_entry.runtime_data

    with pytest.raises(AttributeError):
        await coordinator.async_write(coordinator.device.ventilation, "nonsense", 1)


async def test_a_failed_write_does_not_stop_the_queue(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
    instant_writes: None,
) -> None:
    """A worker that died of one bad write would hang every later caller."""
    await setup_entry(hass, wgt_entry)
    coordinator = wgt_entry.runtime_data
    ventilation = coordinator.device.ventilation

    unit.fail_write(FAN_SPEED, ModbusConnectionError("connection reset"))
    with pytest.raises(UpdateFailed):
        await coordinator.async_write(ventilation, "fan_speed", 3)

    unit.fail_write(FAN_SPEED, None)

    async with asyncio.timeout(5):
        await coordinator.async_write(ventilation, "shock_ventilation", 1)
        await coordinator.async_write(ventilation, "fan_speed", 3)
    await coordinator.async_wait_for_writes()

    assert unit.holding[SHOCK_VENTILATION] == 1
    assert unit.holding[FAN_SPEED] == 3


# -- lifecycle ----------------------------------------------------------------


async def test_unloading_with_a_write_in_flight_does_not_hang(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
    instant_writes: None,
) -> None:
    """Unload cancels the worker rather than waiting out a silent device.

    A device that has stopped answering without closing the socket is the case
    that would strand the queue, so the write here never returns at all.
    """
    await setup_entry(hass, wgt_entry)
    coordinator = wgt_entry.runtime_data
    ventilation = coordinator.device.ventilation

    in_flight = asyncio.Event()
    never = asyncio.Event()

    async def hang(address: int, values: list[int]) -> None:
        in_flight.set()
        await never.wait()

    queued = [
        asyncio.create_task(coordinator.async_write(ventilation, "fan_speed", 3)),
        asyncio.create_task(
            coordinator.async_write(ventilation, "shock_ventilation", 1)
        ),
    ]

    with patch.object(unit, "write_registers", hang):
        async with asyncio.timeout(5):
            await in_flight.wait()

        # The queue is now stuck on a request that will never come back.
        async with asyncio.timeout(10):
            assert await hass.config_entries.async_unload(wgt_entry.entry_id)

    # And the callers were released rather than left waiting on a dead worker.
    async with asyncio.timeout(5):
        results = await asyncio.gather(*queued, return_exceptions=True)
    assert all(isinstance(result, asyncio.CancelledError) for result in results)


async def test_a_write_superseded_during_its_readback_is_not_retried(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
    instant_writes: None,
    retrying: None,
) -> None:
    """The stale value must not be re-sent on top of a newer one.

    The readback is an await, so a newer value can arrive while it is in
    flight. Here it arrives exactly then, which is the narrow window the check
    before the re-write closes.
    """
    await setup_entry(hass, wgt_entry)
    coordinator = wgt_entry.runtime_data
    ventilation = coordinator.device.ventilation
    original = unit.holding[FAN_SPEED]

    recorded = writes(unit)

    def swallow_the_first(event: WriteEvent) -> None:
        if event.address == FAN_SPEED and len(recorded) == 1:
            unit.holding[FAN_SPEED] = original

    unit.on_write(swallow_the_first)

    read_holding = unit.read_holding_registers
    superseded = False

    async def supersede_mid_readback(address: int, count: int) -> list[int]:
        nonlocal superseded
        result = await read_holding(address, count)
        if address == FAN_SPEED and count == 1 and not superseded:
            superseded = True
            hass.async_create_task(
                coordinator.async_write(ventilation, "fan_speed", 4)
            )
        return result

    with patch.object(unit, "read_holding_registers", supersede_mid_readback):
        await coordinator.async_write(ventilation, "fan_speed", 3)
        await coordinator.async_wait_for_writes()
        await hass.async_block_till_done()
        await coordinator.async_wait_for_writes()

    # The swallowed 3 was never re-sent; only the newer 4 followed it.
    assert [event.values for event in recorded] == [[3], [4]]
    assert unit.holding[FAN_SPEED] == 4


async def test_by_default_a_swallowed_write_is_reported_and_left_alone(
    hass: HomeAssistant,
    mock_modbus,
    unit: MockModbusUnit,
    wgt_entry: MockConfigEntry,
    instant_writes: None,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The shipped settings observe rather than re-write.

    Re-writing assumes a register reads back what was written to it, which is
    unproven on the hardware, so the default reads back, reports the mismatch
    and sends nothing more. No ``retrying`` fixture here on purpose: this is
    the behaviour as configured.
    """
    await setup_entry(hass, wgt_entry)
    coordinator = wgt_entry.runtime_data
    original = unit.holding[FAN_SPEED]

    recorded = writes(unit)

    def swallow(event: WriteEvent) -> None:
        if event.address == FAN_SPEED:
            unit.holding[FAN_SPEED] = original

    unit.on_write(swallow)

    await coordinator.async_write(coordinator.device.ventilation, "fan_speed", 3)
    await coordinator.async_wait_for_writes()

    assert [event.address for event in recorded] == [FAN_SPEED]
    assert "but the device still reads" in caplog.text

    # The readback still happened; it is the re-write that is off.
    assert any(
        event.address == FAN_SPEED and event.count == 1
        for event in unit.read_events
    )
