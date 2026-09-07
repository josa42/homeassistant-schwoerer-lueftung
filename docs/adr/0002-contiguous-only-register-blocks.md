# 0002. Contiguous-only register blocks

- Status: accepted
- Date: 2026-09-07

## Context

Reading one register per request is slow: a fully subscribed poll in 1.x cost
40 or more round trips, because its planner grouped only strictly consecutive
addresses. `modbus-connection` plans better by default. It merges fields across
gaps up to `max_gap` (16 registers), and merges freely inside any declared
`register_ranges`. On our map that collapses the poll to roughly ten block reads.

It also does not work. The firmware refuses any block that contains an address
it does not implement. Asked for holding 100 to 112, one block over the fields
at 100-104 and 110-112 bridging the unimplemented 105-109, a real WGT answers
exception code 2, Illegal Data Address, and the entire read fails. The separate
0-1023 probe recorded in `docs/undocumented-registers.md` confirms the same
strictness at single-register granularity.

The strict grouping in 1.x was therefore load-bearing rather than a naive
limitation, and nothing in the code said so. The first draft of the rewrite
replaced it with gap-based merging and the device rejected the very first read.

## Considered Options

- Default `max_gap`, with `register_ranges` declared per component.
- Declare a field for every implemented address so the gaps disappear.
- `max_gap = 1` and no `register_ranges` anywhere.

## Decision

We will set `max_gap = 1` on the shared `SchwoererComponent` base class, and no
component will declare `register_ranges`.

Every block is then a contiguous run of registers we declared a field for, so a
read can never reach an address the device does not implement. `register_ranges`
is excluded because inside a range the planner merges freely again, which is
exactly what must not happen. That holds for `Room` too: its fields are placed
by `index` with `stride=1` per field, and the contiguous runs that produces are
left to `max_gap` like everywhere else.

Two tests pin the behaviour: `test_every_address_read_has_a_field_behind_it`
and `test_reads_never_bridge_a_gap`, both in `tests/test_device.py`.

## Consequences

The poll costs more round trips than the planner would otherwise use: 32 blocks
for a WGT with a ground heat exchanger and rooms, against the 22 of the draft
that did not work. It is still fewer than 1.x, whose grouping ran over a sparser,
entity-driven register set.

Adding a register in the middle of a declared run silently merges it into the
neighbouring block, which is fine. Adding one that is not implemented on some
firmware breaks that whole block instead of one field, so new fields belong in
their own component when their availability is uncertain, per
[0003](0003-components-by-hardware-subsystem.md).

Anyone reading the component definitions has to be told not to reach for
`register_ranges` as an optimisation. That warning is in the module docstring and
on the base class, because the failure it prevents appears only on hardware and
never against the mock.
