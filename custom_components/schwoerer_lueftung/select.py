"""Select platform for Schwörer Lüftung."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SchwoererConfigEntry
from .entity import SchwoererEntity, SchwoererEntityDescription

# Betriebsart.
OPERATION_MODE = {
    0: "off",
    1: "manual",
    2: "winter",
    3: "summer",
    4: "summer_exhaust",
}

# Manuelle Luftstufe.
FAN_SPEED = {
    0: "0",
    1: "1",
    2: "2",
    3: "3",
    4: "4",
    5: "automatic",
    6: "linear",
}

# Heiz-Kühlfunktion.
HEATING_COOLING_FUNCTION = {
    0: "off",
    1: "heating",
    2: "cooling",
    3: "auto_outdoor_temp",
    4: "auto_digital_input",
}


@dataclass(frozen=True, kw_only=True)
class SchwoererSelectEntityDescription(
    SchwoererEntityDescription, SelectEntityDescription
):
    """Describe a select over a coded, writable device field."""

    options_map: dict[int, str]


COMMON_SELECTS: tuple[SchwoererSelectEntityDescription, ...] = (
    SchwoererSelectEntityDescription(
        key="operation_mode", subsystem="ventilation", options_map=OPERATION_MODE
    ),
    SchwoererSelectEntityDescription(
        key="fan_speed", subsystem="ventilation", options_map=FAN_SPEED
    ),
)

HEATING_SELECTS: tuple[SchwoererSelectEntityDescription, ...] = (
    SchwoererSelectEntityDescription(
        key="heating_cooling_function",
        subsystem="heating",
        options_map=HEATING_COOLING_FUNCTION,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SchwoererConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data

    descriptions = list(COMMON_SELECTS)
    if coordinator.has_heating():
        descriptions.extend(HEATING_SELECTS)

    async_add_entities(
        SchwoererSelect(coordinator, description) for description in descriptions
    )


class SchwoererSelect(SchwoererEntity, SelectEntity):
    """A select over a coded, writable device field."""

    entity_description: SchwoererSelectEntityDescription

    def __init__(
        self, coordinator, description: SchwoererSelectEntityDescription
    ) -> None:
        super().__init__(coordinator, description)
        self._attr_options = list(description.options_map.values())

    @property
    def current_option(self) -> str | None:
        value = self._value
        if value is None:
            return None
        return self.entity_description.options_map.get(value)

    async def async_select_option(self, option: str) -> None:
        for value, name in self.entity_description.options_map.items():
            if name == option:
                await self._async_write(value)
                return
