# Changelog

Releases before 2.0.0 are described on the
[releases page](https://github.com/josa42/homeassistant-schwoerer-lueftung/releases).

## 2.0.0 (unreleased)

A rewrite onto the Modbus architecture Home Assistant introduced in 2026.9.
Entities keep their IDs, so history, automations and dashboards survive the
upgrade and no reconfiguration is needed.

### Breaking

- **Home Assistant 2026.9.0 or newer is required.** The integration depends on
  the `modbus` integration and asks it for a unit.
- **The connection is shared.** The integration no longer opens its own socket,
  so another integration talking to the same unit no longer competes with it.
  The device serves one Modbus session at a time, which is what made that
  competition hurt.
- **The `raw_value` state attribute is gone from sensors.** It held the
  undecoded register word, which the diagnostics download now carries for every
  register at once. Anything reading `state_attr(..., 'raw_value')` needs the
  sensor's own state instead. `entity_type` and `room_number` are unchanged.
- **The "enable all sensors by default" setup question is gone.** Home Assistant
  applied it only when an entity was first registered, so the answer given
  during setup could never be changed afterwards. Enabling entities in bulk on
  the entity page does the same job and is reversible. Existing installs are
  unaffected: enabled and disabled state lives in the entity registry.

### Added

- A diagnostics download carrying the raw register map, per sub-system, with
  whichever sub-systems answered and whichever refused. It replays into the
  mock backend, so a bug report can become a regression test without hardware.
- The T9 temperature at register 208 and the device clock at 620 to 625, both
  found by probing and both off by default.
- Room entities go unavailable per sub-system. A unit that refuses the heating
  or ground heat exchanger registers now loses those entities alone instead of
  failing the whole poll.

### Changed

- **Most entities now ship enabled.** 66 of 69 are on by default for fresh
  installs. Since the rewrite reads every declared register whether or not an
  entity exists, enabling one costs no Modbus traffic. T9, the device clock and
  the per-room auxiliary heating binary sensor stay off. Existing installs keep
  whatever the entity registry holds.
- **Writes are range-checked before they reach the device.** Room setpoints and
  linear fan power are validated locally, where 1.x let the device reject them.
  The climate entity still clamps rather than raises, so a thermostat card
  asking for an out-of-range value behaves as before.
- **Scaled writes round where 1.x truncated.** On exact 0.1 boundaries the two
  agree; off boundary they differ by a tenth, so 21.99 now writes 220 where 1.x
  wrote 219. That is also more robust to float representation, where 21.9 can
  arrive as `21.900000000000002`.

### Fixed

- Per-room temperature sensors on a WRT came out unnamed. Their translation key
  was never in `strings.json`.
- Long-term statistics work again for the fan level sensors and the three
  countdowns (shock ventilation, device filter, upstream filter). They lost
  their state class back in January 2026, so Home Assistant had stopped
  recording them and raised a repair asking whether to delete the old
  statistics. The error message sensor deliberately keeps no state class: it
  reports a code, and the mean of an error code means nothing.
- `Temperatur T9`, the device clock and the per-room temperature sensor had no
  icon of their own and fell back to the device class default. A test now
  fails if an entity ships without one.
- The ground heat exchanger operating hours sensor is back after the rewrite
  dropped it.
- Room devices link to the ventilation unit by device ID. The identifier tuple
  is deprecated in 2026.9 and made Home Assistant log a warning naming this
  integration.
