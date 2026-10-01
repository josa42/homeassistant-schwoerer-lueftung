# Follow-ups

Deliberately left undone rather than dropped. None of these block a release;
they are recorded so they are not rediscovered from scratch.

- **Turn the readback re-writes on.** `WRITE_READBACK_RETRIES` ships at 0, so a
  write is read back and a mismatch reported without anything being re-sent.
  Verification assumes a register reads back what was written to it, and no
  hardware has confirmed that: a register the firmware self-clears or
  normalises, and the shock ventilation trigger at 111 is the obvious suspect,
  would turn every write to it into three and an error line. Watch the log for
  `but the device still reads`, then raise it to 2. Until then the
  Schreibdisziplin row "Readback-Verifikation mit Retry" is only half met. See
  [ADR 0006](adr/0006-serialized-write-queue.md).
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
