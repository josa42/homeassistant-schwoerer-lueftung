"""Tests for translation strings."""

import json
from pathlib import Path

import pytest

TRANSLATION_FILES = {
    "strings": "custom_components/schwoerer_lueftung/strings.json",
    "en": "custom_components/schwoerer_lueftung/translations/en.json",
    "de": "custom_components/schwoerer_lueftung/translations/de.json",
}

# Valid entity keys that should exist in translation files
VALID_ENTITY_KEYS = {
    "binary_sensor": [
        "alarm_device_filter_dirty",
        "alarm_door_open",
        "alarm_emergency_mode",
        "alarm_external_utility_lock",
        "alarm_heating_module_test",
        "alarm_off_peak_disabled",
        "alarm_pressostat_triggered",
        "alarm_pressure_switch",
        "alarm_supply_air_cold",
        "alarm_supply_voltage_off",
        "alarm_upstream_filter_dirty",
        "alarm_utility_lock",
        "auxiliary_heating_active_room",
        "auxiliary_heating_enabled_room",
        "fan_override",
        "outdoor_damper_state",
        "preheater_1",
        "preheater_2",
        "reheater_state",
    ],
    "climate": [
        "climate_room",
    ],
    "device": [
        "room",
    ],
    "number": [
        "base_temperature_room",
        "linear_fan_power",
    ],
    "select": [
        "fan_speed",
        "heating_cooling_function",
        "operation_mode",
    ],
    "sensor": [
        "bypass_state",
        "current_exhaust_air_flow",
        "current_exhaust_air_rpm",
        "current_fan_level",
        "current_supply_air_flow",
        "current_supply_air_rpm",
        "device_filter_remaining",
        "error_message",
        "exhaust_air_fan_status",
        "ground_heat_exchanger_state",
        "heat_pump_status",
        "operating_hours_auxiliary_heating_house",
        "operating_hours_fan",
        "operating_hours_fan_level_1",
        "operating_hours_fan_level_2",
        "operating_hours_fan_level_3",
        "operating_hours_fan_level_4",
        "operating_hours_ground_heat_exchanger",
        "operating_hours_heat_pump",
        "operating_hours_heat_pump_cooling",
        "operating_hours_preheating_coil",
        "sensor_fan_level",
        "shock_ventilation_remaining",
        "supply_air_fan_status",
        "temperature_t10_outdoor",
        "temperature_t1_after_ground_heat_exchanger",
        "temperature_t2_after_preheating_coil",
        "temperature_t3_before_reheater",
        "temperature_t4_after_reheater",
        "temperature_t5_exhaust_air",
        "temperature_t6_in_heat_exchanger",
        "temperature_t7_evaporator",
        "temperature_t8_condenser",
        "time_program_base_level",
        "time_program_fan_level",
        "upstream_filter_remaining",
    ],
    "switch": [
        "auxiliary_heating_enabled",
        "auxiliary_heating_enabled_room",
        "heat_pump_cooling_enabled",
        "heat_pump_heating_enabled",
        "scheduled_heating_enabled_room",
        "shock_ventilation",
    ],
}


@pytest.fixture
def translations():
    """Load all translation files."""
    translations = {}
    base_path = Path(__file__).parent.parent

    for lang, file_path in TRANSLATION_FILES.items():
        full_path = base_path / file_path
        with open(full_path, "r", encoding="utf-8") as f:
            translations[lang] = json.load(f)

    return translations


class TestTranslationSorting:
    """Test that translation files are sorted alphabetically."""

    def test_translation_files_are_sorted(self, translations):
        """Test that all translation files have their keys sorted alphabetically."""
        for lang, content in translations.items():
            self._assert_dict_is_sorted(content, lang, [])

    def _assert_dict_is_sorted(self, obj, lang, path):
        """Recursively check if dictionary keys are sorted."""
        if isinstance(obj, dict):
            keys = list(obj.keys())
            
            # Check if all keys are numeric strings - if so, sort numerically
            if all(k.lstrip('-').isdigit() for k in keys):
                sorted_keys = sorted(keys, key=lambda x: int(x))
            else:
                sorted_keys = sorted(keys)

            if keys != sorted_keys:
                path_str = ".".join(path) if path else "root"
                pytest.fail(
                    f"{lang}.json: Keys at '{path_str}' are not sorted.\n"
                    f"  Current order: {keys}\n"
                    f"  Expected order: {sorted_keys}"
                )

            # Recursively check nested dictionaries
            for key, value in obj.items():
                self._assert_dict_is_sorted(value, lang, path + [key])


class TestEntityKeyValidation:
    """Test that only valid entity keys exist in translation files."""

    def test_exact_match_of_entity_keys(self, translations):
        """Test that translation files have exactly the expected entity keys."""
        for lang, content in translations.items():
            entities = content.get("entity", {})

            for entity_type, valid_keys in VALID_ENTITY_KEYS.items():
                actual_keys = set(entities.get(entity_type, {}).keys())
                expected_keys = set(valid_keys)

                assert actual_keys == expected_keys, (
                    f"{lang}.json '{entity_type}' keys mismatch:\n"
                    f"  Missing: {sorted(expected_keys - actual_keys)}\n"
                    f"  Extra: {sorted(actual_keys - expected_keys)}"
                )


class TestStateTranslations:
    """Test that state translations are complete across all languages."""

    def test_all_states_have_translations_in_all_languages(self, translations):
        """Test that entities with state translations have all states in all languages."""
        # Get state keys from strings.json (base reference)
        strings_content = translations["strings"]
        entities_with_states = self._get_entities_with_states(strings_content)

        # Check each translation file has same state keys
        for lang in ["en", "de"]:
            lang_content = translations[lang]

            for entity_type, entity_keys in entities_with_states.items():
                for entity_key, state_keys in entity_keys.items():
                    # Check entity exists in translation
                    assert entity_type in lang_content.get("entity", {}), (
                        f"{lang}.json missing entity type '{entity_type}'"
                    )

                    assert entity_key in lang_content["entity"].get(entity_type, {}), (
                        f"{lang}.json missing entity '{entity_type}.{entity_key}'"
                    )

                    # Check state translations exist
                    lang_entity = lang_content["entity"][entity_type][entity_key]
                    assert "state" in lang_entity, (
                        f"{lang}.json missing 'state' for '{entity_type}.{entity_key}'"
                    )

                    # Check all state keys are present
                    lang_state_keys = set(lang_entity["state"].keys())
                    missing_states = state_keys - lang_state_keys
                    extra_states = lang_state_keys - state_keys

                    assert not missing_states and not extra_states, (
                        f"{lang}.json state mismatch for '{entity_type}.{entity_key}':\n"
                        f"  Missing states: {sorted(missing_states)}\n"
                        f"  Extra states: {sorted(extra_states)}"
                    )

    def _get_entities_with_states(self, content):
        """Extract all entities that have state translations."""
        entities_with_states = {}

        for entity_type, entities in content.get("entity", {}).items():
            for entity_key, entity_data in entities.items():
                if isinstance(entity_data, dict) and "state" in entity_data:
                    if entity_type not in entities_with_states:
                        entities_with_states[entity_type] = {}
                    entities_with_states[entity_type][entity_key] = set(
                        entity_data["state"].keys()
                    )

        return entities_with_states
