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
  __init__.py        SchwoererDevice, UpdateReport
  ventilation.py     Ventilation    — 100-145
  temperatures.py    Temperatures   — 200-209 (T5, T6, T10 always; rest WGT-only)
  alarms.py          Alarms         — 230-265
  heating.py         Heating        — WGT-only registers in 114/116/230-234
  operating_hours.py OperatingHours — 800-813
  rooms.py           Room           — 360/400/420/440/460/500, index + stride 1
```

### Component split

The split is driven by [constraint 5](#the-untestable-configuration): a device
that refuses a block fails only the component that asked for it.

| Component        | Registers                          | Present when |
| ---------------- | ---------------------------------- | ------------ |
| `Ventilation`    | 100-104, 110-112, 117-118, 121, 123, 131, 133, 140-145 | always |
| `Temperatures`   | 204, 205, 209                      | always |
| `Alarms`         | 240, 242-248, 250-254, 263, 265    | always |
| `OperatingHours` | 800-804                            | always |
| `GroundHeat`     | 121 state, 200 (T1), 813 hours     | `has_ground_heat_exchanger` |
| `Heating`        | 114, 116, 201-203, 206-207, 230-234, 805-810 | `device_type == wgt` |
| `Room` × N       | 360+i, 400+i, 420+i, 440+i, 460+i, 500+i | per configured room |

`Room` instances go into a `ComponentGroup` so N rooms still cost six block
reads, not 6×N.

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
- Every component declares `register_ranges`, so a block read never bridges
  from a mapped cluster into unmapped addresses. The default `max_gap` of 16
  would otherwise bridge, for example, 254 → 263.
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

- Regenerate `docs/registers.md` from the component definitions.
- README: note the 2026.9 requirement and the shared connection.

## Deliberately out of scope

- Publishing the device layer to PyPI (only needed for Core submission).
- Probing at setup to auto-detect subsystems and retire the `device_type` /
  `has_ground_heat_exchanger` config-flow questions. The component split makes
  this a small follow-up.
- Splitting readings from settings onto separate coordinator intervals.
- Removing the `raw_value` attribute, made redundant by diagnostics.
