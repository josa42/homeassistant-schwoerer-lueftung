# 0004. Preserve entity identity across the rewrite

- Status: accepted
- Date: 2026-09-07
- Superseded in part by: [0005](0005-drop-the-raw-value-state-attribute.md),
  the `raw_value` state attribute only

## Context

The rewrite replaces roughly sixty hand-written entity classes, built on a
shared `abstract.py`, with frozen `EntityDescription` dataclasses carrying a
`value_fn` and the name of the component they read from.

Everything user-visible hangs off the identifiers those classes produced.
Entity `unique_id` is `f"{entry_id}_{key}"` where `key` came from `REG_KEYS`,
except `RoomClimate`, which used `f"{entry_id}_room_{n}_climate"`. Translation
keys are the same names, with `_room` appended for room entities. The
`entity_type`, `room_number` and `raw_value` state attributes were added
deliberately and feed the Lit card under `frontend/`. Config entry data has its
own shape: `host`, `device_type`, `rooms`, `has_ground_heat_exchanger`.

A changed `unique_id` loses all recorded history for that entity and silently
breaks any automation or dashboard referring to it. Users will not be reading
release notes closely enough to repair that by hand.

## Considered Options

- Take the rewrite as the moment to clean up the naming, and migrate the entity
  registry and config entries.
- Keep the 1.x identifiers exactly, and let the new code shape itself around
  them.

## Decision

We will keep the identifiers. Component field names are chosen to reproduce the
old `REG_KEYS` values character for character, the climate entity keeps its
special case, and `SchwoererEntity` derives `unique_id` and `translation_key`
from the description key with the same rules the abstract base used. The three
state attributes stay. There is no config entry migration, because entry data
is unchanged.

## Consequences

An upgrade from 1.x keeps history, automations and dashboards intact, and no
migration code has to be written, tested or maintained.

The price is that the field names in `device/components.py` are not free. They
are a published interface, so a name that reads awkwardly stays awkward, and
renaming one later is a breaking change that needs a registry migration. The
constraint is easy to violate by accident, so it is recorded in the module
docstring of `entity.py` and covered by tests over the translation files.

`raw_value` on temperature sensors is the one deviation we accepted: 1.x exposed
the undecoded register word (`215`), and it is now the decoded value (`21.5`).
Every other sensor is unscaled, so its `raw_value` is unchanged. The undecoded
map now lives in the diagnostics download, which is what it was really being used
for.
