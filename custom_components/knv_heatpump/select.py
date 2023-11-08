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
    config_entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Setup sensors from a config entry created in the integrations UI."""
    config = config_entry.data
    coordinator = KNVCoordinator(hass, config)

    await coordinator.async_config_entry_first_refresh()

    data = coordinator.data
    write = []

    for data in coordinator.data:
        if knv.getType(data) == knv.Type.SELECT:
            write.append(data)

    async_add_entities(
        KnvSelect(coordinator, idx, data) for idx, data in enumerate(write)
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

            for data in self.data["listentries"]:
                self._attr_options.append(data["text"])

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if self.coordinator.data["path"] == self.data["path"]:
            self.data["value"] = self.coordinator.data["value"]

            self.coordinator.logger.info(self._attr_name)

            self.async_write_ha_state()
