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
        "preheater_1",
        "preheater_2",
        "reheater_state",
    ],
    "climate": [
        "room_climate",
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
        "outdoor_damper_state",
        "sensor_fan_level",
        "shock_ventilation_remaining",
        "supply_air_fan_status",
        "temp_t10_outdoor",
        "temp_t1_after_ground_heat_exchanger",
        "temp_t2_after_preheating_coil",
        "temp_t3_before_reheater",
        "temp_t4_after_reheater",
        "temp_t5_exhaust_air",
        "temp_t6_in_heat_exchanger",
        "temp_t7_evaporator",
        "temp_t8_condenser",
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

                assert actual_keys == expected_keys, \
                    f"{lang}.json '{entity_type}' keys mismatch:\n" \
                    f"  Missing: {sorted(expected_keys - actual_keys)}\n" \
                    f"  Extra: {sorted(actual_keys - expected_keys)}"
