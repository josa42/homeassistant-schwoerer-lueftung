# 0005. Drop the `raw_value` state attribute

- Status: accepted
- Date: 2026-09-07
- Supersedes in part: [0004](0004-preserve-entity-identity-across-the-rewrite.md),
  the `raw_value` state attribute only

## Context

[0004](0004-preserve-entity-identity-across-the-rewrite.md) decided to carry
1.x entity identity through the rewrite untouched: `unique_id`s, translation
keys, and the `entity_type`, `room_number` and `raw_value` state attributes.

It recorded one accepted deviation. In 1.x, `raw_value` held the undecoded
register word straight off the wire, so a temperature read `215`. The rewrite
moves decoding into the field definition, so the same attribute would read
`21.5`. The name was preserved while the meaning changed.

That deviation is the problem. A template doing
`state_attr('sensor.t10', 'raw_value') / 10` keeps working, keeps producing a
number, and produces one ten times too small, with nothing to notice. Removing
the attribute breaks the same template loudly, in a release the user is already
reading notes for because it requires a new Home Assistant.

The attribute has also lost its purpose. It existed so a user could see what the
device actually returned, one entity at a time. 2.0 ships a diagnostics download
carrying the undecoded map for every register at once, which is the same
information in the form a bug report needs.

## Considered Options

- Keep `raw_value` with its new decoded meaning, as 0004 decided.
- Keep it undecoded, by reaching past the field to the register word.
- Remove it.

## Decision

We will remove `raw_value` from sensor state attributes.

`SchwoererSensor` loses its `extra_state_attributes` override entirely, so every
entity in the integration reports the same attribute set from `SchwoererEntity`.
A test asserts the attribute is absent, so it cannot return by accident.

This replaces one clause of 0004 and nothing else. The rest of that record still
governs and stays `accepted`: every `unique_id`, entity ID and translation key
still reproduces its 1.x value exactly, `entity_type` and `room_number` stay,
and there is still no config entry migration.

## Consequences

Anything reading `raw_value` breaks, and breaks visibly rather than silently
misreading a value. The changelog names the attribute and points at the sensor's
own state as the replacement. It is a breaking change in a release that is
already breaking, which is the cheapest moment to make one.

Per-entity access to the undecoded word is gone. Recovering it means the
diagnostics download rather than a template, which is worse for automation and
better for diagnosis. Nothing in this repository consumed the attribute; a
dashboard card outside it might, and that cannot be checked from here.

0004 keeps its status because its core decision survives. A reader who lands on
it sees in the header that one clause moved here, which is the price of having
bundled four decisions into one record. Finer-grained ADRs would not have needed
the pointer.
