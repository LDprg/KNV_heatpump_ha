"""Platform for sensor integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
)
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
        if knv.getType(data) == knv.Type.NUMBER:
            if not data["path"] in coordinator.paths:
                coordinator.paths.append(data["path"])
                
                async_add_entities(
                    [KnvNumber(coordinator, data)]
                )

    coordinator.async_add_listener(_async_measurement_listener)


class KnvNumber(CoordinatorEntity, NumberEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, data):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.data: Any = data

        self.name = self.data["path"] + " - " + self.data["name"]
        self.unique_id = self.data["path"]

        if "value" in self.data:
            self.native_value = self.data["value"]

        self.native_max_value = float(self.data["max"])
        self.native_min_value = float(self.data["min"])
        
        self.native_step = max(1.0, float(self.data["step"]))
        
        self.native_unit_of_measurement = self.data["unit"]

        if self.data["type"] == 6:
            self.device_class = NumberDeviceClass.TEMPERATURE
        elif self.data["type"] == 8:
            self.device_class = NumberDeviceClass.ENERGY_STORAGE
        elif self.data["type"] == 4:
            self.device_class = NumberDeviceClass.DURATION

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if self.coordinator.data["path"] == self.data["path"]:
            self.data["value"] = self.coordinator.data["value"]
            self.native_value = self.data["value"]

            self.coordinator.logger.info(self.name)

            self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        if bool(self.data["writeable"]) is True:
            await self.coordinator.socket.send(self.data["path"], value)
        else:
            raise NotImplementedError()
