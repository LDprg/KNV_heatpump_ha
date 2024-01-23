"""Platform for sensor integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)


from .coordinator import KNVCoordinator

from . import const as knv


async def async_setup_entry(
    hass: HomeAssistant,
    _config_entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Setup sensors from a config entry created in the integrations UI."""
    coordinator: KNVCoordinator = hass.data[knv.DOMAIN]["coord"]

    select = []

    for data in coordinator.data:
        if knv.getType(data) == knv.Type.SELECT:
            select.append(data)

    async_add_entities(
        KnvSelect(coordinator, idx, data) for idx, data in enumerate(select)
    )


class KnvSelect(CoordinatorEntity, SelectEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, idx, data=None):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=idx)
        self.idx: int = idx
        self.data: Any = data

        if self.data is not None:
            self._attr_name = self.data["path"] + " - " + self.data["name"]
            self._attr_unique_id = self.data["path"]

            self._attr_options = []
            for data in self.data["listentries"]:
                self._attr_options.append(data["text"])

            if "value" in self.data:
                self._attr_current_option = self.knv_get_option(
                    self.data["value"])

    def knv_get_option(self, value):
        """Translates value to text"""
        for data in self.data["listentries"]:
            if int(value) == int(data["value"]):
                self.coordinator.logger.warn(
                    "%s: %s -- %s", self.data["path"], value, data["text"])
                return data["text"]

    def knv_get_value(self, option):
        """Translates value to text"""
        for data in self.data["listentries"]:
            if option == data["text"]:
                return data["value"]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if self.coordinator.data["path"] == self.data["path"]:
            self.data["value"] = self.coordinator.data["value"]

            self._attr_current_option = self.knv_get_option(self.data["value"])

            self.coordinator.logger.info(self._attr_name)

            self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if self.date["writeable"] is True:
            await self.coordinator.socket.send(self.data["path"], self.knv_get_value(option))
        else:
            raise NotImplementedError()