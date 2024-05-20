"""Platform for sensor integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import KNVCoordinator

from . import const as knv


async def async_setup_entry(
    hass: HomeAssistant,
    _config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup sensors from a config entry created in the integrations UI."""
    coordinator: KNVCoordinator = hass.data[knv.DOMAIN]["coord"]

    def _async_measurement_listener() -> None:
        """Listen for new measurements and add sensors if they did not exist."""
        for data in self.coordinator.data:
            if knv.getType(data) == knv.Type.SELECT:
                if not data["path"] in coordinator.paths:
                    coordinator.paths.append(data["path"])

                    async_add_entities(
                        [KnvSelect(coordinator, data["path"])]
                    )

    coordinator.async_add_listener(_async_measurement_listener)


class KnvSelect(CoordinatorEntity, SelectEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, path):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)

        self.path = path

        self._attr_name = self.path + " - " + self.get_data()["name"]
        self._attr_unique_id = self.path

        self._attr_options = []
        for data in self.get_data()["listentries"]:
            self._attr_options.append(data["text"])

        if "value" in self.get_data():
            self._attr_current_option = self.knv_get_option(
                self.get_data()["value"])

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_current_option = self.knv_get_option(
            self.get_data()["value"])
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if bool(self.get_data()["writeable"]) is True:
            await self.coordinator.socket.send(self.path, self.knv_get_value(option))
        else:
            raise NotImplementedError()

    def get_data():
        return self.coordinator.data[self.path]

    def knv_get_option(self, value):
        """Translates value to text"""
        for data in self.get_data()["listentries"]:
            if int(value) == int(data["value"]):
                return data["text"]

    def knv_get_value(self, option):
        """Translates value to text"""
        for data in self.get_data()["listentries"]:
            if option == data["text"]:
                return data["value"]
