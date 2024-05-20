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
        for data in self.coordinator.data:
            if knv.getType(data) == knv.Type.NUMBER:
                if not data["path"] in coordinator.paths:
                    coordinator.paths.append(data["path"])

                    async_add_entities(
                        [KnvNumber(coordinator, data["path"])]
                    )

    coordinator.async_add_listener(_async_measurement_listener)


class KnvNumber(CoordinatorEntity, NumberEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, path):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.path = path

        self._attr_name = self.path + " - " + self.get_data()["name"]
        self._attr_unique_id = self.path

        if "value" in self.get_data():
            self._attr_native_value = self.get_data()["value"]

        self._attr_native_max_value = float(self.get_data()["max"])
        self._attr_native_min_value = float(self.get_data()["min"])

        self._attr_native_step = max(1.0, float(self.get_data()["step"]))

        self._attr_native_unit_of_measurement = self.get_data()["unit"]

        if self.get_data()["type"] == 6:
            self._attr_device_class = NumberDeviceClass.TEMPERATURE
        elif self.get_data()["type"] == 8:
            self._attr_device_class = NumberDeviceClass.POWER
        elif self.get_data()["type"] == 4:
            self._attr_device_class = NumberDeviceClass.DURATION

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.get_data()["value"]
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        if bool(self.get_data()["writeable"]) is True:
            await self.coordinator.socket.send(self.path, value)
        else:
            raise NotImplementedError()

    def get_data():
        return self.coordinator.data[self.path]
