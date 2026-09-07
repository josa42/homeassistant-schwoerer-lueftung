# Follow-ups

Deliberately left out of the 2.0 rewrite. None of these block a release; they
are recorded so they are not rediscovered from scratch.

- **Probe at setup to auto-detect sub-systems.** Reading one register per
  optional component would settle whether the device has heating and a ground
  heat exchanger, and retire the `device_type` and `has_ground_heat_exchanger`
  questions from the config flow. The component split makes this small: see
  [ADR 0003](adr/0003-components-by-hardware-subsystem.md).
- **Split readings from settings onto separate coordinator intervals.**
  Everything is on one 30-second poll. Setpoints and schedules do not change on
  their own and could be read far less often.
- **Publish the device layer to PyPI.** Only needed if the integration is ever
  submitted to Home Assistant Core, which requires the device library to live
  outside the integration. `device/` imports nothing from Home Assistant, so the
  split is already possible.
