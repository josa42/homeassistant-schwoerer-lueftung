# CLAUDE.md

## Documentation languages

The user documentation exists in English and German, side by side:

- `README.md` and `README.de.md`
- `docs/manual_installation.md` and `docs/manual_installation.de.md`

English is the main version. A change to one of these files goes into its
German counterpart in the same commit. The German version names entities and
states as `custom_components/schwoerer_lueftung/translations/de.json` does, so
they match what users see in Home Assistant.

Everything else stays English only: `CHANGELOG.md`, `docs/registers.md`,
`docs/adr/`, `docs/references/`, `docs/todo.md`, code comments and commit
messages.
