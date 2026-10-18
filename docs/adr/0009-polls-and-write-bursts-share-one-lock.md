# 0009. Polls and write bursts share one lock

- Status: accepted
- Date: 2026-10-18

## Context

[0006](0006-serialized-write-queue.md) moved writes into a queue so a poll no
longer interleaves with a burst of writes. It made sure the queue's own poll
comes after the burst. The coordinator's scheduled poll, every 30 seconds, knew
nothing of the queue and could still start while a burst was going out.

A burst of fifteen writes takes about 7.5 seconds at the shipped pacing, so a
consumer that writes in bursts met the scheduled poll in roughly one burst out
of four. Interleaved reads are the failure 0006 exists to remove.

## Considered Options

- Pace the whole connection with `unit.set_message_spacing`.
- Have the poll wait for the queue to drain.
- One `asyncio.Lock`, held by the poll and by the queue for a whole burst.

## Decision

We will share one lock in the coordinator. The poll takes it around the device
read, the diagnostics read takes it too, and the queue's worker holds it while
it drains. The worker releases it before asking for its own poll, which takes
the same lock.

Pacing the connection was rejected in 0006 for slowing every poll. Waiting for
the queue to drain covers the poll but not the reverse: a burst starting during
a poll would still interleave with it.

`test_a_scheduled_poll_waits_for_the_burst` pins the behaviour. It fails
without the lock.

## Consequences

A write that arrives during a poll waits for the poll to finish before it goes
out, which is up to a poll's duration. A long stream of writes delays the
scheduled poll for as long as it lasts.

Two probes of the same refused block can no longer run at once, since a
diagnostics read and a poll take turns, so
[0008](0008-skip-registers-the-firmware-refuses.md) needs no guard against
recording a field twice.
