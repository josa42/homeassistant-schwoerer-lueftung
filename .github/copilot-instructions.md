# GitHub Copilot Instructions

## Commit Workflow

### Always Commit Changes

When completing tasks that modify files:
- **Always commit changes** - Don't leave uncommitted work
- Use clear, descriptive commit messages
- Include the co-author attribution (see below)

### Amending Commits

When it makes sense to amend (refine, fix typos, add forgotten files):
- **DO amend** commits that haven't been pushed yet
- **NEVER amend** commits that have already been pushed
- Use `git commit --amend` for local-only commits

Example when to amend:
- ✅ Just committed, then realized a typo in the commit message
- ✅ Just committed, but forgot to add a file that belongs to the same change
- ✅ Just committed, but need to adjust formatting in the same logical change
- ❌ Commit was already pushed to remote
- ❌ Commit is more than a few minutes old and work has moved on

## Translation Guidelines

### Always Provide English and German Translations

When adding new translatable strings (entities, options, errors, etc.):
- **Always provide both English and German translations**
- **Use British English** (not American English)
- Store translations in the respective JSON files
- Never hardcode strings in Python code

**British vs American English:**
- ✅ British: "Colour", "Optimise", "Behaviour", "Centre", "Metre"
- ❌ American: "Color", "Optimize", "Behavior", "Center", "Meter"

### Use Schwörer Terminology

When naming entities and writing descriptions:
- **Use the official Schwörer terminology** from the Modbus documentation
- **Reference `docs/registers.md`** for correct wording and terms
- Maintain consistency with existing entity names
- Use technical terms as defined by the manufacturer

**Example:** Use "Vorheizregister" (Pre-Heater) not "Vorheizer" or "Pre-heater"

### Umlaut Handling

**For user-facing strings (translations, display names):**
- ✅ **USE umlauts**: ä, ö, ü, ß
- Example: "Außentemperatur", "Lüftung", "Wärmetauscher"

**For technical strings (keys, IDs, file names, Python variables):**
- ✅ **REPLACE umlauts** with ASCII equivalents:
  - ä → ae
  - ö → oe
  - ü → ue
  - ß → ss
- Example: `aussentemperatur`, `lueftung`, `waermetauscher`

**Examples:**

```python
# Python code - no umlauts
translation_key = "vorheizregister_zustand"
unique_id = f"{entry.entry_id}_nhr_zustand"

# Translation file - use umlauts
{
  "entity": {
    "binary_sensor": {
      "nhr_zustand": {
        "name": "NHR Zustand"  # User sees umlauts
      }
    }
  }
}
```

### Translation File Locations

```
custom_components/schwoerer_lueftung/
├── strings.json                          # English translations (default)
└── translations/
    ├── en.json                          # English translations
    └── de.json                          # German translations
```

### Translation Structure

Both files should maintain the same structure:

**English (`strings.json` and `translations/en.json`):**
```json
{
  "config": {
    "step": {
      "user": {
        "title": "Configure Schwörer Ventilation",
        "data": {
          "host": "IP Address",
          "port": "Port"
        }
      }
    }
  },
  "entity": {
    "sensor": {
      "outdoor_temperature": {
        "name": "Outdoor Temperature"
      }
    }
  }
}
```

**German (`translations/de.json`):**
```json
{
  "config": {
    "step": {
      "user": {
        "title": "Schwörer Lüftung konfigurieren",
        "data": {
          "host": "IP-Adresse",
          "port": "Port"
        }
      }
    }
  },
  "entity": {
    "sensor": {
      "outdoor_temperature": {
        "name": "Außentemperatur"
      }
    }
  }
}
```

### Guidelines for Translations

- ✅ **DO**: Add translations for both languages when creating new entities
- ✅ **DO**: Use British English spelling and terminology
- ✅ **DO**: Update both JSON files when modifying existing strings
- ✅ **DO**: Use proper German terms (e.g., "Außentemperatur" not "Aussentemperatur")
- ✅ **DO**: Use German umlauts (ä, ö, ü, ß) in user-facing translations
- ✅ **DO**: Replace umlauts with ASCII (ae, oe, ue, ss) in technical keys/IDs
- ✅ **DO**: Use Schwörer terminology from docs/registers.md
- ✅ **DO**: Keep translation keys consistent across languages
- ❌ **DON'T**: Use American English spellings
- ❌ **DON'T**: Leave English text in German translations
- ❌ **DON'T**: Hardcode translatable strings in Python code
- ❌ **DON'T**: Add translations to only one language
- ❌ **DON'T**: Use umlauts in Python identifiers or file names

### Common German HVAC Terms

- Ventilation = Lüftung
- Temperature = Temperatur
- Fan = Lüfter / Ventilator
- Fan Level = Luftstufe
- Operation Mode = Betriebsart
- Heating = Heizen
- Cooling = Kühlen
- Outdoor = Außen
- Indoor = Innen
- Supply Air = Zuluft
- Exhaust Air = Abluft
- Heat Exchanger = Wärmetauscher
- Filter = Filter

## Commit Message Format

Always include a co-author attribution in commit messages:

```
Co-authored-by: GitHub Copilot <github-copilot@github.com>
```

### Example

```
Fix MODEL undefined error in platform files

- Import MODEL_WGT and MODEL_WRT from const in all platform files
- Add dynamic model computation based on coordinator.has_heating()
- Replace undefined MODEL with computed model variable
- Fixes NameError in binary_sensor, number, select, sensor, and switch platforms

Co-authored-by: GitHub Copilot <github-copilot@github.com>
```

## Guidelines

- Add the co-author line as the last line of every commit message
- Separate the co-author line from the commit body with a blank line
- Use the exact format: `Co-authored-by: GitHub Copilot <github-copilot@github.com>`
- Always commit completed work - don't leave changes uncommitted
- Amend local commits when it makes sense, but never amend pushed commits
- Always provide English (British) and German translations for new strings
- Store translations in the respective JSON files
- Use Schwörer terminology from docs/registers.md
- Use umlauts in user-facing strings, ASCII replacements in technical identifiers
