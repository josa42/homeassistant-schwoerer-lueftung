# 0003. Components split by hardware subsystem

- Status: accepted
- Date: 2026-09-07

## Context

The register map is not the same on every unit. Heating registers exist on a
WGT and not on a WRT, the ground heat exchanger registers exist only where the
hardware is installed, and the clock at 620-625 and the T9 temperature at 208
were found by probing rather than read from the datasheet.

Since 1.x created heating and ground heat exchanger entities conditionally,
those registers have never been read on a device that lacks them. There is no
evidence for how a WRT answers such a read. Given that the firmware answers
Illegal Data Address for anything it does not implement (see
[0002](0002-contiguous-only-register-blocks.md)), the plausible outcome is a
failed read, and if that read is part of one large poll then a WRT owner loses
every sensor, not just the heating ones.

We cannot resolve this by testing. Nobody on the project has a WRT, or a unit
without a ground heat exchanger.

## Decision

We will make each subsystem its own `Component`, and treat a component as the
unit of failure.

`SchwoererDevice.async_update` polls each component separately, catches
`ModbusError` per component, and records the outcome in `UpdateReport.updated`
or `UpdateReport.failed`. Every entity description names the `subsystem` it
reads from, and the entity goes unavailable unless that name is in `updated`,
so a subsystem the hardware does not have costs its own entities and nothing
else.

Optional components are instantiated from the config entry: `Heating` when
`device_type` is WGT, `GroundHeatExchanger` when the user declared one, one
`Room` per configured room. The room components go into a `ComponentGroup` so
that N rooms still cost six block reads rather than six per room.

Registers found by probing get the same treatment for the same reason.
`UndocumentedTemperatures` and `Clock` are separate components, and their
entities ship disabled by default: this is one firmware's behaviour on one unit,
and a device without them must not lose documented sensors alongside them.

A diagnostics download exposes the raw register map per component, so an owner
of the hardware we cannot test can supply real data. `modbus-connection` replays
such a dump into its mock, which turns a bug report into a regression test with
no hardware involved.

## Consequences

An unsupported subsystem degrades to unavailable entities instead of an empty
integration, and the diagnostics give us the evidence to fix it properly. If the
firmware turns out to be tolerant after all, the split costs a few extra round
trips and nothing else.

Against that, the component boundary is now a compatibility decision rather than
a tidiness one, and a poll that partially fails is a state entities have to
handle. `available` is no longer just the coordinator's success flag, and every
entity description has to name its subsystem correctly or it will report the
wrong availability. `test_a_refused_subsystem_fails_alone` and
`test_entities_go_unavailable_only_with_their_own_subsystem` cover the
boundary.

The split is also what will let us retire the `device_type` and
`has_ground_heat_exchanger` questions from the config flow later, by probing each
optional component once at setup. That is deliberately out of scope here.
