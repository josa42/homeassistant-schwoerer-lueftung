# 0001. Shared Modbus units and the modbus-connection device model

- Status: accepted
- Date: 2026-09-07

## Context

Version 1.x opened its own TCP socket with `pymodbus.ModbusTcpClient` and kept
the register map as a `dict[int, str]` next to hand-written transforms.

Three problems followed from that. The WGT serves one Modbus session at a time,
so a second integration, or a probe run from a shell, competes with us for the
device and one of the two fails. `ModbusTcpClient` is synchronous, so every read
and write had to be pushed through `hass.async_add_executor_job`. And the
register map carried no types, units or validators, which left decoding and
range checks scattered across the entity classes.

Home Assistant 2026.9 changes the terms. The `modbus` integration now hands out
`ModbusUnit` objects over connections it shares between integrations, and ships
`modbus-connection`, a backend-neutral connection abstraction with a
device-modelling framework on top.

## Considered Options

- Keep the private `pymodbus` client and fix the read planner in place.
- Swap the transport to `ModbusUnit` but keep the existing register dictionary.
- Adopt both the shared unit and the `modbus-connection` device model.

## Decision

We will adopt both, and release it as 2.0.0 with a minimum of Home Assistant
2026.9.0.

The integration declares `modbus` as a dependency and asks for its unit through
`async_get_unit`, so the connection is shared and reconnection is the library's
job. `modbus/client.py`, `modbus/registers.py` and `modbus/transforms.py` are
deleted.

The register map becomes a device layer under `device/`, holding a
`SchwoererDevice` and its components. That layer imports nothing from Home
Assistant, so it can be tested against the library's mock backend alone, and the
integration keeps the coordinator, entities and config flow above it.

The device layer stays inside the integration rather than moving to PyPI. Custom
integrations are exempt from Core's separate-library rule, and the layering keeps
the option open for the day that matters.

## Consequences

Two integrations, or an integration and a diagnostic probe, can now address the
device without fighting over the socket. Reads and writes are async end to end,
and the executor hops are gone. Decoding, units and write validation live on the
fields, so entities carry presentation only.

The cost is a hard version floor. Anyone below 2026.9 cannot install 2.0.0, and
the API this rests on cannot be imported before that release. We also inherit a
dependency we do not control: read planning, retries and reconnection are the
library's behaviour now, and tuning them means arguing with upstream rather than
editing our own client. The first draft of this rewrite found that out the hard
way, which is [0002](0002-contiguous-only-register-blocks.md).

Writes needed one accommodation. The WGT rejects Write Single Register (FC06)
and answers only Write Multiple Registers (FC16), so every writable field carries
`force_fc16=True` rather than getting a custom write path.
