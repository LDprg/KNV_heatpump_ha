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

        data = coordinator.data
        if knv.getType(data) == knv.Type.SELECT:
            if not data["path"] in coordinator.paths:
                coordinator.paths.append(data["path"])

                async_add_entities(
                    [KnvSelect(coordinator, data)]
                )

    coordinator.async_add_listener(_async_measurement_listener)


class KnvSelect(CoordinatorEntity, SelectEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, data):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.data: Any = data

        self.name = self.data["path"] + " - " + self.data["name"]
        self.unique_id = self.data["path"]

        self.options = []
        for data in self.data["listentries"]:
            self.options.append(data["text"])

        if "value" in self.data:
            self.current_option = self.knv_get_option(
                self.data["value"])

    def knv_get_option(self, value):
        """Translates value to text"""
        for data in self.data["listentries"]:
            if int(value) == int(data["value"]):
                return data["text"]

    def knv_get_value(self, option):
        """Translates value to text"""
        for data in self.data["listentries"]:
            if option == data["text"]:
                return data["value"]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data

        if data["path"] == self.data["path"]:
            self.data["value"] = data["value"]

            self.current_option = self.knv_get_option(self.data["value"])

            self.coordinator.logger.debug(self.name)

            self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if bool(self.data["writeable"]) is True:
            await self.coordinator.socket.send(self.data["path"], self.knv_get_value(option))
        else:
            raise NotImplementedError()
