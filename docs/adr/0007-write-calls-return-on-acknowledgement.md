# 0007. Write calls return on acknowledgement

- Status: accepted
- Date: 2026-10-01

## Context

[0006](0006-serialized-write-queue.md) puts a queue in front of every write and
verifies each one by reading it back. That raises a question the old code never
had to answer: how far should `Coordinator.async_write` await?

The old call awaited `component.write()` and raised `UpdateFailed` on a
`ModbusError`, so a consumer learned that a write had failed. Every call site
awaits it, and none writes optimistic state: `entity.py`'s `_async_write` funnels
`number`, `switch` and `select`, and `climate.py` calls the coordinator directly
for its two extra fields.

Awaiting the verification as well is the strongest guarantee, and it is what the
first draft of this work proposed. It has two costs. A bundle of fifteen fields
would block its caller for the whole queue, which at the shipped pacing is
several seconds, and the hang risks of the queue would sit on the caller's await
rather than inside the worker. Those risks are real but they are not deadlock:
the worker never waits on the queue it is serving, the readback is issued by the
worker inline rather than enqueued, and the transport's lock is held per request,
so no cycle exists. What can happen is a lost wakeup, from a worker that dies
with callers pending, or a superseded write whose future nobody resolves.

## Considered Options

- Await the write and its verification, raising when the retries are exhausted.
- Await only that the request went out, and verify behind the caller.
- Return as soon as the write is queued.

## Decision

We will have `async_write` return once the device has acknowledged the request.

Readback, re-writing and the poll for the burst happen in the worker, after the
caller has gone. A mismatch that survives is logged at error level, naming the
field, the register, and the words expected and read, and the poll at the end of
the burst publishes the device's real value so no entity keeps reporting a value
the device never took.

This keeps the error contract unchanged for everything a consumer can act on. A
`ModbusError` still becomes `UpdateFailed`, and the `ValueError` a field's range
validator raises still surfaces synchronously, because the validator runs inside
`component.write()` on the caller's own await. An `AttributeError` for an unknown
or read-only field is unchanged too.

Returning merely on being queued is rejected: it would discard that contract,
including the validator errors, which are pure Python and cost nothing to raise.

## Consequences

A caller waits for one round trip rather than for a poll, so setting a single
value returns sooner than it did before.

The write a consumer cannot distinguish is the one the device acknowledges and
then discards. It no longer fails the service call. It is logged and, once
re-writing is turned on, re-sent, and the burst's poll corrects the state. This
is the deliberate price of the decision, and it is the exact failure 0006 exists
to catch, so it is worth stating plainly that the catching is now by log and
state rather than by exception.

The two lost-wakeup risks move into the worker, where they are bounded: the
worker resolves every future in a `finally`, releases pending callers if it dies
or is cancelled, and lets the next write start a fresh worker.
`test_three_writes_to_one_field_write_once` and
`test_a_failed_write_does_not_stop_the_queue` exist for exactly these.

Verification is no longer something a caller can wait for. A test, or anything
else that needs the queue finished, uses `Coordinator.async_wait_for_writes()`,
which exists because Home Assistant's `async_block_till_done` deliberately does
not wait for background tasks.
