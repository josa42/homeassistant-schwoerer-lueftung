# Modbus modernization

Adopt the Modbus architecture introduced in Home Assistant 2026.9
([release notes](https://www.home-assistant.io/blog/2026/09/02/release-20269/#modernizing-modbus),
[developer docs](https://developers.home-assistant.io/docs/modbus/introduction),
[modbus-connection docs](https://home-assistant-libs.github.io/modbus-connection/)).

Target release: **2.0.0** (breaking — requires Home Assistant 2026.9.0).

## Why

Home Assistant now hands out Modbus *units* over connections it shares between
integrations, and ships [`modbus-connection`](https://home-assistant-libs.github.io/modbus-connection/)
— a backend-neutral connection abstraction plus a device-modelling framework.

For this integration that means:

- **Shared connection.** Today we open our own socket. Two integrations talking
  to one device compete for it; the WGT answers one request at a time.
- **Native async.** `pymodbus.ModbusTcpClient` is synchronous, so every read and
  write goes through `hass.async_add_executor_job`. A `ModbusUnit` is async.
- **Better read planning.** `ModbusClient._get_grouped_subscriptions` groups only
  *strictly consecutive* addresses (`client.py:134-136`), so registers 114 and
  116 are two separate reads. A fully-subscribed poll is 40+ round trips. The
  library's planner merges across gaps up to `max_gap` (default 16), which turns
  our map into ~10 block reads.
- **Typed device model.** The register map becomes typed Python attributes with
  units and validators attached, instead of a `dict[int, str]` plus hand-written
  transforms.

## Scope

Transport swap **and** device-modelling rewrite, kept inside
`custom_components/schwoerer_lueftung/`. No separate PyPI package — custom
integrations are exempt from Core's separate-library rule, though the layering
below keeps that option open.

## Hard constraints

1. **Entity unique_ids must not change.** Existing ids are
   `f"{entry_id}_{key}"` where `key` is a `REG_KEYS` value (`abstract.py:64`),
   except `RoomClimate`, which is `f"{entry_id}_room_{n}_climate"`
   (`climate.py:65-67`). Component field names are chosen to reproduce these
   exactly. A changed id loses all history and breaks user automations.
2. **`entity_type`, `room_number` and `raw_value` state attributes stay.** The
   first two were added deliberately in `cb4cd0a` and `0640465` and are assumed
   to feed the Lit card under `frontend/`.
3. **Translation keys must not change.** Global entities use the field name;
   room entities use the field name with `_room` appended
   (`abstract.py:159-163` strips the trailing `_\d+`).
4. **No config entry migration.** Entry data (`host`, `device_type`, `rooms`,
   `has_ground_heat_exchanger`, `enable_all_sensors_by_default`) is unchanged.

## Architecture

Three layers, per the
[integration-structure guide](https://home-assistant-libs.github.io/modbus-connection/home-assistant/integration/):

```
modbus-connection            (shipped by the modbus integration)
  └── schwoerer_lueftung/device/    device object + Components, no HA imports
        └── schwoerer_lueftung/     coordinator, entities, config flow
```

### `device/` — the device object

Follows the
[device-object pattern](https://home-assistant-libs.github.io/modbus-connection/patterns/library/):
takes a `ModbusUnit`, exposes sub-systems as attributes, returns an
`UpdateReport` from each poll. No Home Assistant imports, so it is testable
against the mock backend alone.

```
device/
  __init__.py     SchwoererDevice, UpdateReport
  components.py   the whole register map, one Component per sub-system
```

The components live in one file rather than one file each: they are short, and
keeping the map in a single place is what makes it readable as a datasheet.

### Component split

The split is driven by [the untestable configuration](#the-untestable-configuration):
a device that refuses a block fails only the component that asked for it.

| Component                  | Registers                                                 | Present when |
| -------------------------- | --------------------------------------------------------- | ------------ |
| `Ventilation`              | 100-104, 110-112, 117-118, 123, 131, 133, 140-145         | always |
| `Temperatures`             | 204, 205, 209                                             | always |
| `UndocumentedTemperatures` | 208 (T9)                                                  | always |
| `Alarms`                   | 240, 242-248, 250-254, 263, 265                           | always |
| `OperatingHours`           | 800-804                                                   | always |
| `Heating`                  | 114, 116, 201-203, 206-207, 230-234, 805-810              | `device_type == wgt` |
| `GroundHeatExchanger`      | 121, 200, 813                                             | `has_ground_heat_exchanger` |
| `Clock`                    | 620-625                                                   | always |
| `Room` × N                 | 360+i, 400+i, 420+i, 440+i, 460+i, 500+i                  | per configured room |

`UndocumentedTemperatures` and `Clock` hold registers found by probing rather
than from the datasheet — see `undocumented-registers.md`. They are kept apart
from the documented components on the same principle as the hardware-dependent
ones: this is one firmware's behaviour on one unit, and a device without them
must not lose documented sensors alongside them. Both entities ship disabled.

`Room` instances go into a `ComponentGroup` so N rooms still cost six block
reads, not 6×N.

### Block formation: `max_gap = 1`, no `register_ranges`

**The firmware refuses any block containing an address it does not implement.**
Asked for holding 100-112 — one block over the fields at 100-104 and 110-112,
bridging the unimplemented 105-109 — a real WGT answers exception code 2,
Illegal Data Address, and the whole read fails.

So `SchwoererComponent` sets `max_gap = 1`, which merges only fields at
adjacent addresses. Every block is then a contiguous run of registers we
declared a field for, and a read can never reach an address the device does not
have. No component declares `register_ranges`: inside a range the planner
merges freely again, which is exactly what must not happen.

This is what the 1.x client did by grouping strictly consecutive addresses
(`client.py:134-136`). That was load-bearing, not a naive limitation — the
first draft of this rewrite replaced it with gap-based merging and the device
rejected the very first read.

Two tests pin it: one asserts every address read has a field declared behind
it, the other that the specific rejected block is never formed again.

### Measured read counts

Against the mock, per 30-second poll:

| Configuration                   | Blocks | Registers |
| ------------------------------- | ------ | --------- |
| WGT + ground heat exchanger + 3 rooms | 32 | 78 |
| WGT + ground heat exchanger + 17 rooms | 32 | 162 |
| WRT, no ground heat exchanger, no rooms | 15 | 42 |

Room count changes the registers read but not the number of round trips. More
blocks than the first draft's 22, but that draft did not work on the hardware.
Still fewer than 1.x, which fragmented the same map into 40+ reads because its
grouping ran over a sparser, entity-driven register set.

### Room placement

`room_reg(base, n) = base + (n - 1)` — each field steps by 1 per room, so a room
is *not* a contiguous block. This is the
[interleaved-by-type case](https://home-assistant-libs.github.io/modbus-connection/modelling/placement/),
handled with `index` and a per-field `stride=1`, not `repeating_group`:

```python
class Room(Component):
    register_ranges = ((360, 376), (400, 416), (420, 436),
                       (440, 456), (460, 476), (500, 516))

    current_temperature = gauge(360, 0.1, stride=1, unit="°C")
    target_temperature = gauge(400, 0.1, stride=1, unit="°C",
                               writable=True, force_fc16=True)
    base_temperature = gauge(420, 0.1, stride=1, unit="°C",
                             writable=True, force_fc16=True)
    auxiliary_heating_enabled = boolean(440, stride=1,
                                        writable=True, force_fc16=True)
    auxiliary_heating_active = boolean(460, stride=1)
    scheduled_heating_enabled = boolean(500, stride=1,
                                        writable=True, force_fc16=True)
```

Only configured rooms are instantiated, so a two-room house reads two addresses
per block, not seventeen.

### Writes

The WGT rejects Write Single Register (FC06) and needs Write Multiple Registers
(FC16) even for one register — the reason for `client.py:83-84`. Every writable
field carries `force_fc16=True`
([`fields.py:96`](https://github.com/home-assistant-libs/modbus-connection/blob/main/src/modbus_connection/model/fields.py),
[`_writing.py:56`](https://github.com/home-assistant-libs/modbus-connection/blob/main/src/modbus_connection/model/_writing.py)),
so no custom write path is needed.

### Transforms

`modbus/transforms.py` disappears. `to_temperature` (signed 16-bit ÷ 10) is
`gauge(addr, 0.1)`; the enum maps become `enum(addr, {...})`; the alarm
registers become `boolean(addr)`.

## The untestable configuration

Entities for heating and the ground heat exchanger are created conditionally
(`sensor.py:111,123`, `binary_sensor.py:77`, `climate.py:38`, `number.py:34`,
`select.py:32`, `switch.py:38`), so **those registers have never been read on a
device that lacks them.** There is no evidence for how a WRT, or a unit without
a ground heat exchanger, answers a read of them.

The design hedges rather than guesses:

- Optional subsystems are their own `Component`, so `_async_poll` catches the
  `ModbusError` and records it in `UpdateReport.failed` instead of failing the
  whole poll.
- `max_gap = 1` means a block never covers an address without a declared field,
  so a component reads only its own registers and nothing speculative. See
  [Block formation](#block-formation-max_gap--1-no-register_ranges) — this
  turned out to be a hard requirement of the firmware, not just a hedge.
- Entities go unavailable via `report.failed`, per subsystem.
- A diagnostics download exposes the raw register map, which is how a WRT owner
  can supply real data. `modbus-connection`'s `load_raw()` replays such a dump
  straight into the mock, so a bug report can become a regression test with no
  hardware.

If the firmware turns out to be tolerant, the declared ranges cost a couple of
extra round trips and nothing else. If it is strict, they are what makes it work.

## Steps

### 1. Development environment

- Bump the pinned Home Assistant in `venv/` to 2026.9+ — the new API cannot be
  imported before that.
- `requirements_test.txt`: drop `pymodbus`, add `pytest-homeassistant-custom-component`
  matching 2026.9.
- `hacs.json`: `homeassistant` `2026.1.0` → `2026.9.0`.
- `manifest.json`: `after_dependencies: ["modbus"]` → `dependencies: ["modbus"]`;
  drop the `pymodbus` requirement; version → `2.0.0`.

### 2. The device layer

- Add `device/` with the components above, ported from `modbus/registers.py`.
  Field names must reproduce the `REG_KEYS` values exactly.
- Add `SchwoererDevice` with `async_update()`, `async_read_raw()` and the
  `UpdateReport` dataclass.
- Delete `modbus/client.py`, `modbus/registers.py`, `modbus/transforms.py`.

### 3. Wiring

- `config_flow.validate_input` → `async_get_temporary_unit`.
- `__init__.async_setup_entry` → `async_get_unit`; `hass.data[DOMAIN][entry_id]`
  → `entry.runtime_data` with a typed `ConfigEntry` alias.
- `Coordinator` returns `UpdateReport`; maps `ModbusError` → `UpdateFailed`;
  drops the executor jobs, `connect`/`disconnect`, and the whole subscription
  mechanism including the side-effecting `get_data` (`coordinator.py:90-91`).
- **No entry reload on connection loss** — reconnection is automatic.
- One coordinator on the existing 30 s interval. Splitting readings from
  settings onto separate intervals is a later, independent change.

### 4. Entities

- Replace the ~60 one-off entity classes with frozen `EntityDescription`
  dataclasses carrying `value_fn` and `report_name`.
- `available` = `super().available and report_name in coordinator.data.updated`.
- Preserve unique_ids, translation keys and the three state attributes.
- Incidental fix: `climate.py:73` sets `_attr_target_temperature_room_step`,
  which is not a Home Assistant attribute — should be
  `_attr_target_temperature_step`.

### 5. Diagnostics

- `diagnostics.py` with `async_get_config_entry_diagnostics` returning
  `updated`, `failed` and the raw register map from `async_read_raw()`.

### 6. Tests

- Delete `test_modbus_client.py` and `test_transforms.py` — they test deleted code.
- Adopt the `modbus-connection` pytest plugin (auto-registered via entry point;
  no conftest wiring). Fixtures: `mock_modbus_unit`, `mock_modbus_connection`.
- Component tests: seed `mock_modbus_unit.holding`, assert decoded values.
- **Assert on `read_events`** to pin the block plan, so `register_ranges` is
  enforced by test rather than by hope — in particular that a WRT-shaped
  configuration issues no read into the heating registers.
- Rewrite `test_coordinator.py` against the async flow.
- `test_init.py` and `test_translations.py` largely survive.

### 7. Docs

- README: note the 2026.9 requirement and the shared connection.
- `docs/registers.md` is the transcribed vendor datasheet, not a generated
  artifact, so it stays as it is.

## Verified against real hardware

A WGT at firmware level as of 2026-09-07, no ground heat exchanger, 6 rooms.

- **Reads.** All sub-systems answer; every gauge cross-checked raw → decoded;
  every coded register maps to a known option; room placement lands on the
  right addresses. `async_read_raw()` returned exactly 93 registers — the field
  count, with nothing read beyond what is declared.
- **Writes.** One write, register 103 back to the value it already held, over
  the production path. The wire frame carried function code `0x10` and the
  device echoed it without the error bit. See `device/components.py`.
- **Reconnection.** Observed unplanned: the device serves one Modbus session at
  a time, so a probe holding the socket made setup fail with
  `ConfigEntryNotReady`. Home Assistant retried after 10 s and succeeded, with
  no reload — which is the designed behaviour.

Still unexercised: every writable register other than 103, since they all have
physical effects — operation mode and fan speed change ventilation, the heating
switches change heating. The encoder and validators behind them are covered by
tests against the mock.

## Known deviations from 1.x behaviour

- **`raw_value` on temperature sensors.** 1.x exposed the undecoded register
  word (`215`); it is now the decoded value (`21.5`). Every other sensor is
  unscaled, so its `raw_value` is unchanged. The undecoded map now lives in the
  diagnostics download, which is what it was really for.
- **Write validation.** Room setpoints and linear fan power are range-checked
  by the field before the write reaches the wire, where 1.x let the device
  reject them. The climate entity still clamps rather than raises, so a
  thermostat card asking for an out-of-range value behaves as before.
- **Scaled writes round where 1.x truncated.** Encoding moved from
  `int(value * 10)` in the entity to the library's `gauge` encoder. On exact
  0.1 boundaries they agree; off-boundary they differ by a tenth — 21.99 now
  writes 220 where 1.x wrote 219. Rounding is the better behaviour, and it is
  more robust to float representation, where 21.9 can arrive as
  `21.900000000000002`.

## Known issue, not addressed here

`DeviceInfo(via_device=...)` is deprecated in 2026.9 in favour of
`via_device_id`, and Home Assistant logs a warning naming this integration. It
keeps working until 2027.8. Fixing it needs the registry's device id rather
than the identifier tuple, which is a separate change.

## Deliberately out of scope

- Publishing the device layer to PyPI (only needed for Core submission).
- Probing at setup to auto-detect subsystems and retire the `device_type` /
  `has_ground_heat_exchanger` config-flow questions. The component split makes
  this a small follow-up.
- Splitting readings from settings onto separate coordinator intervals.
- Removing the `raw_value` attribute, made redundant by diagnostics.
