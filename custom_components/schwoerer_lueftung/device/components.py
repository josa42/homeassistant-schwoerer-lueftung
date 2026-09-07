"""The Schwörer WGT/WRT register map, as modbus-connection components.

This module is the datasheet: every address the integration reads lives here,
next to its scaling, unit and writability. It has no Home Assistant imports, so
it can be tested against the mock backend alone.

Field names are the keys the entity layer builds unique_ids and translation keys
from. **Renaming a field renames the entity**, which loses its history, so the
names here reproduce the pre-2.0 ``REG_KEYS`` values exactly.

## Why every read is a run of declared fields

This firmware refuses any block containing an address it does not implement.
Asked for holding 100-112 — a single block over the fields at 100-104 and
110-112, bridging the unimplemented 105-109 — it answers exception code 2,
Illegal Data Address, and the whole read fails.

So :class:`SchwoererComponent` sets ``max_gap = 1``, which merges only fields
at adjacent addresses. Every block is then a contiguous run of registers we
declared a field for, and a read can never reach an address the device does not
have. Declaring ``register_ranges`` would undo this — inside a range the
planner merges freely again — so no component declares one.

This is what the pre-2.0 client did by grouping strictly consecutive addresses.
That was load-bearing, not a limitation.

## How the components are split

A device answering some sub-systems and not others should not lose the ones it
does answer. The heat pump registers (a WRT has none) and the ground heat
exchanger registers (not every unit has one) are therefore their own
components, so a refusal fails that component alone and the rest of the poll
still lands.

## Why writes force FC16

The device rejects Write Single Register (FC06) and answers only Write Multiple
Registers (FC16), even for a single register. Every writable field therefore
sets ``force_fc16=True``.
"""

from __future__ import annotations

from datetime import datetime as _datetime

from modbus_connection.model import Component, gauge, integer


class SchwoererComponent(Component):
    """Base for every sub-system, fixing how blocks may be formed.

    ``max_gap = 1`` merges only fields at adjacent addresses, so a block never
    covers a register we did not declare a field for. The device rejects any
    block spanning an address it does not implement, so this is a correctness
    requirement, not a tuning knob. Do not add ``register_ranges`` to a
    subclass: a range lets the planner merge freely inside it and reintroduces
    exactly the reads this prevents.
    """

    max_gap = 1


# Value ranges the device accepts, enforced before a write reaches the wire.
LINEAR_FAN_POWER_MIN = 30
LINEAR_FAN_POWER_MAX = 100
ROOM_TEMPERATURE_MIN = 10.0
ROOM_TEMPERATURE_MAX = 30.0


def _within[T: (int, float)](low: T, high: T):
    """Return a write validator rejecting values outside ``low``-``high``."""

    def validate(value: T) -> T:
        if not low <= value <= high:
            raise ValueError(f"{value} is outside the accepted range {low}-{high}")
        return value

    return validate


class Ventilation(SchwoererComponent):
    """Fan control and air-path state — the registers every unit serves.

    114 and 116 (heat pump, reheater) and 121 (ground heat exchanger) sit
    between these addresses but belong to optional hardware. No field is
    declared for them here, and ``max_gap = 1`` will not merge across the gaps
    they leave, so this component never reads them.
    """

    operation_mode = integer(100, writable=True, force_fc16=True)
    """Betriebsart: 0=off, 1=manual, 2=winter, 3=summer, 4=summer exhaust."""

    fan_speed = integer(101, writable=True, force_fc16=True)
    """Manuelle Luftstufe: 0-4 = level, 5=automatic, 6=linear."""

    current_fan_level = integer(102)
    """Aktuelle Luftstufe."""

    linear_fan_power = integer(
        103,
        unit="%",
        writable=_within(LINEAR_FAN_POWER_MIN, LINEAR_FAN_POWER_MAX),
        force_fc16=True,
    )
    """Manuelle lineare Luftleistung, 30-100%."""

    fan_override = integer(104)
    """Luftstufen-Überschreibung: 0=inactive, 1=active."""

    time_program_base_level = integer(110)
    """Zeitprogramm Basis-Luftstufe."""

    shock_ventilation = integer(111, writable=True, force_fc16=True)
    """Stoßlüftung: 0=inactive, 1=active."""

    shock_ventilation_remaining = integer(112, unit="min")
    """Restlaufzeit Stoßlüftung."""

    supply_air_fan_status = integer(117)
    """Status Gebläse Zuluft: 0=disabled, 1=startup, 2=active, 5=standby, 6=error."""

    exhaust_air_fan_status = integer(118)
    """Status Gebläse Abluft: 0=disabled, 1=startup, 2=active, 5=standby, 6=error."""

    bypass_state = integer(123)
    """Bypass Zustand: 0=closed, 1=open (cooling), 2=open (heating)."""

    outdoor_damper_state = integer(131)
    """Aussenklappe Zustand: 0=closed, 1=open."""

    preheater_state = integer(133)
    """Vorheizregister Zustand: 0=off, 1=VHR 1, 2=VHR 2, 3=VHR 1 & 2."""

    time_program_fan_level = integer(140)
    """Luftstufe Zeitprogramm."""

    sensor_fan_level = integer(141)
    """Luftstufe Sensoren."""

    current_supply_air_flow = integer(142, unit="%")
    """Luftleistung aktuell Zuluft."""

    current_exhaust_air_flow = integer(143, unit="%")
    """Luftleistung aktuell Abluft."""

    current_supply_air_rpm = integer(144, unit="rpm")
    """Aktuelle Drehzahl Zuluft."""

    current_exhaust_air_rpm = integer(145, unit="rpm")
    """Aktuelle Drehzahl Abluft."""


class Temperatures(SchwoererComponent):
    """The air-path sensors every unit has.

    200-203 and 206-207 belong to the heat pump and the ground heat exchanger
    and are read by :class:`Heating` and :class:`GroundHeatExchanger`.
    """

    temperature_t5_exhaust_air = gauge(204, 0.1, unit="°C")
    """T5 Abluft."""

    temperature_t6_in_heat_exchanger = gauge(205, 0.1, unit="°C")
    """T6 im Wärmetauscher."""

    temperature_t10_outdoor = gauge(209, 0.1, unit="°C")
    """T10 Aussen."""


class UndocumentedTemperatures(SchwoererComponent):
    """Air-path sensors the datasheet omits, found by probing a real WGT.

    The datasheet numbers its sensors T1-T8 and T10, skipping 208. That address
    is implemented and reads a temperature sitting among its neighbours, so it
    is almost certainly the missing T9. What it measures is unknown.

    Read as its own component rather than folded into :class:`Temperatures`:
    this is one firmware's behaviour on one unit, and a device without it must
    not lose the documented sensors alongside it. It costs no extra round trip,
    since 208 is adjacent to T10 and would share its block either way.
    """

    temperature_t9 = gauge(208, 0.1, unit="°C")
    """T9 — undocumented; position in the air path unknown."""


class Clock(SchwoererComponent):
    """The unit's own real-time clock, 620-625. Not in the datasheet.

    Confirmed by reading it three times three seconds apart and watching it
    track the wall clock. Its own component for the same reason as
    :class:`UndocumentedTemperatures`.
    """

    year = integer(620)
    month = integer(621)
    day = integer(622)
    hour = integer(623)
    minute = integer(624)
    second = integer(625)

    @property
    def datetime(self) -> _datetime | None:
        """The device's clock, or None until read or if it reads nonsense.

        Naive: the unit keeps local time with no zone, so the caller attaches
        one. A device with a dead clock can report an out-of-range date, which
        ``datetime`` would raise on, so that is folded into None.
        """
        parts = (self.year, self.month, self.day, self.hour, self.minute, self.second)
        if any(part is None for part in parts):
            return None
        try:
            return _datetime(*parts)  # type: ignore[arg-type]
        except ValueError:
            return None


class Alarms(SchwoererComponent):
    """Fault and maintenance registers.

    Read on every unit. Some are only meaningful on a WGT and the entity layer
    surfaces them accordingly, but that is a presentation choice, not a claim
    about which registers the device serves.
    """

    error_message = integer(240)
    """Fehlermeldung."""

    alarm_pressure_switch = integer(242)
    """Meldung Druckwächter aktiv."""

    alarm_utility_lock = integer(243)
    """EVU-Sperre aktiv."""

    alarm_door_open = integer(244)
    """Tür offen."""

    alarm_device_filter_dirty = integer(245)
    """Gerätefilter verschmutzt."""

    alarm_upstream_filter_dirty = integer(246)
    """Vorgelagerter Filter verschmutzt."""

    alarm_off_peak_disabled = integer(247)
    """Niedertarif abgeschaltet."""

    alarm_supply_voltage_off = integer(248)
    """Versorgungsspannung abgeschaltet."""

    alarm_pressostat_triggered = integer(250)
    """Pressostat ausgelöst."""

    alarm_external_utility_lock = integer(251)
    """EVU-Sperre extern aktiv."""

    alarm_heating_module_test = integer(252)
    """Heizmodul Testbetrieb aktiv."""

    alarm_emergency_mode = integer(253)
    """Notbetrieb aktiv."""

    alarm_supply_air_cold = integer(254)
    """Zuluft zu kalt."""

    upstream_filter_remaining = integer(263, unit="d")
    """Restlaufzeit vorgelagerter Filter."""

    device_filter_remaining = integer(265, unit="d")
    """Restlaufzeit Gerätefilter."""


class OperatingHours(SchwoererComponent):
    """Hour counters for the fan, which every unit has."""

    operating_hours_fan = integer(800, unit="h")
    """Betriebsstunden Gebläse."""

    operating_hours_fan_level_1 = integer(801, unit="h")
    """Betriebsstunden Luftstufe 1."""

    operating_hours_fan_level_2 = integer(802, unit="h")
    """Betriebsstunden Luftstufe 2."""

    operating_hours_fan_level_3 = integer(803, unit="h")
    """Betriebsstunden Luftstufe 3."""

    operating_hours_fan_level_4 = integer(804, unit="h")
    """Betriebsstunden Luftstufe 4."""


class Heating(SchwoererComponent):
    """Heat pump, reheater and auxiliary heating — WGT only.

    Read as its own component so a WRT, which has none of this hardware, fails
    only here.
    """

    heat_pump_status = integer(114)
    """Status Wärmepumpe: 0=off, 5=heating, 49=cooling."""

    reheater_state = integer(116)
    """NHR Zustand: 0=inactive, 1=active."""

    temperature_t2_after_preheating_coil = gauge(201, 0.1, unit="°C")
    """T2 nach VHR."""

    temperature_t3_before_reheater = gauge(202, 0.1, unit="°C")
    """T3 vor NE."""

    temperature_t4_after_reheater = gauge(203, 0.1, unit="°C")
    """T4 nach NE."""

    temperature_t7_evaporator = gauge(206, 0.1, unit="°C")
    """T7 Verdampfer."""

    temperature_t8_condenser = gauge(207, 0.1, unit="°C")
    """T8 Kondensator."""

    heating_cooling_function = integer(230, writable=True, force_fc16=True)
    """Heiz-Kühlfunktion: 0=off, 1=heating, 2=cooling, 3=auto outdoor, 4=auto digital."""

    heat_pump_heating_enabled = integer(231, writable=True, force_fc16=True)
    """Wärmepumpe Heizen: 0=off, 1=enabled."""

    heat_pump_cooling_enabled = integer(232, writable=True, force_fc16=True)
    """Wärmepumpe Kühlen: 0=off, 1=enabled."""

    auxiliary_heating_enabled = integer(234, writable=True, force_fc16=True)
    """Zusatzheizung Haus: 0=off, 1=enabled."""

    operating_hours_heat_pump = integer(805, unit="h")
    """Betriebsstunden Wärmepumpe."""

    operating_hours_heat_pump_cooling = integer(806, unit="h")
    """Betriebsstunden Wärmepumpe Kühlen."""

    operating_hours_preheating_coil = integer(809, unit="h")
    """Betriebsstunden Vorheizregister."""

    operating_hours_auxiliary_heating_house = integer(810, unit="h")
    """Betriebsstunden Zusatzheizung Haus."""


class GroundHeatExchanger(SchwoererComponent):
    """Erdwärmetauscher — present only where the installation has one."""

    ground_heat_exchanger_state = integer(121)
    """EWT Zustand: 0=off/closed, 1=heating, 2=cooling."""

    temperature_t1_after_ground_heat_exchanger = gauge(200, 0.1, unit="°C")
    """T1 nach EWT."""

    operating_hours_ground_heat_exchanger = integer(813, unit="h")
    """Betriebsstunden EWT."""


class Room(SchwoererComponent):
    """One of up to 17 rooms.

    A room is *not* a contiguous block: register addresses are grouped by
    field, so room *n* reads ``base + (n - 1)`` for each of the six fields.
    That is the interleaved-by-type layout, so each field carries
    ``stride=1`` and the instance is placed with ``index=room_number`` —
    a ``repeating_group``, which steps a whole block at once, cannot express it.

    The ranges are stated at the addresses the layout actually reads, covering
    all 17 slots, because an indexed field shifts on its own rather than the
    block shifting with it.
    """

    current_temperature = gauge(360, 0.1, stride=1, unit="°C")
    """Aktuelle Temperatur Raum."""

    target_temperature = gauge(
        400,
        0.1,
        stride=1,
        unit="°C",
        writable=_within(ROOM_TEMPERATURE_MIN, ROOM_TEMPERATURE_MAX),
        force_fc16=True,
    )
    """Solltemperatur Raum."""

    base_temperature = gauge(
        420,
        0.1,
        stride=1,
        unit="°C",
        writable=_within(ROOM_TEMPERATURE_MIN, ROOM_TEMPERATURE_MAX),
        force_fc16=True,
    )
    """Grundtemperatur Raum."""

    auxiliary_heating_enabled = integer(440, stride=1, writable=True, force_fc16=True)
    """Zusatzheizung Freigabe Raum: 0=blocked, 1=enabled."""

    auxiliary_heating_active = integer(460, stride=1)
    """Zusatzheizung aktiv Raum: 0=inactive, 1=active."""

    scheduled_heating_enabled = integer(500, stride=1, writable=True, force_fc16=True)
    """Freigabe Zeitprogramm Heizen Raum: 0=disabled, 1=enabled."""
