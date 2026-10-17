# 0008. Skip registers the firmware refuses

- Status: accepted
- Date: 2026-10-18

## Context

[0002](0002-contiguous-only-register-blocks.md) reads every block as a run of
declared fields, because the firmware refuses a block containing any address it
does not implement. [0003](0003-components-by-hardware-subsystem.md) splits the
map into components so that one refused block fails one sub-system.

That assumed every firmware serves the same registers within a sub-system. It
does not. A VentCube sold by Bauinfocenter refuses 142-145 (air flow and fan
speed). Those sit in the block 140-145, so the whole of `Ventilation` failed,
fan control included. The config flow tested the connection by reading all of
`Ventilation`, so setup failed with "cannot connect" on a device that was
answering. Another user's unit started working after a firmware update, which
fits the same cause.

We cannot know in advance which firmware serves what, and splitting every
uncertain register into its own component costs a round trip each on every
unit.

## Considered Options

- A component per uncertain register run, like `UndocumentedTemperatures`.
- Probe every register when the integration loads, and read only what answered.
- Probe on demand: when a block is refused with Illegal Data Address, read its
  fields one at a time, drop the refused ones with `restrict_fields`, and retry.

## Decision

We will probe on demand, in `SchwoererDevice`.

A unit that serves everything never sees a probe, so it costs nothing there. A
refusal costs one read per field of the refused block, once per load, and the
answer comes back immediately rather than as a timeout.

Only exception code 2, Illegal Data Address, counts as proof that a register is
missing. Any other error while probing propagates as before, and nothing is
dropped until every field of the component has been probed, so a timeout or a
dropped link never costs a field.

What was dropped is kept on the device object and not persisted. A firmware
update that adds registers is picked up on the next reload.

The config flow reads only 100-104, the fan control every firmware serves, and
tells a refused read apart from a failed connection.

## Consequences

Entities are still created for dropped fields and stay unavailable, so entity
IDs and history do not depend on the firmware. The diagnostics download lists
dropped fields under `unserved`, which tells us what a given firmware lacks.

A sub-system no longer fails on Illegal Data Address alone. Tests that simulate
a failing sub-system use another exception code, such as Server Device Failure.

A register refused only some of the time would be dropped until the next
reload. We have seen no firmware do that.
