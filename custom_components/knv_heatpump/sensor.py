"""Platform for sensor integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
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
        for path in coordinator.data:
            if knv.getType(coordinator.data[path]) == knv.Type.SENSOR:
                knv.LOGGER.warn("Found: %s", path)
                if not path in coordinator.paths:
                    coordinator.paths.append(path)

                    knv.LOGGER.warn("Add: %s", path)

                    async_add_entities(
                        [KnvSensor(coordinator, path)]
                    )

    coordinator.async_add_listener(_async_measurement_listener)


class KnvSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, path):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.path = path

        knv.LOGGER.warn("Init: %s", path)

        self._attr_name = self.path + " - " + self.get_data()["name"]
        self._attr_unique_id = self.path

        if self.data["unit"]:
            self._attr_native_unit_of_measurement = self.get_data()["unit"]

        if self.get_data()["type"] == 6 or self.get_data()["type"] == 8:
            try:
                self._attr_native_value = float(self.get_data()["value"])
            except TypeError:
                self._attr_native_value = None
            except ValueError:
                self._attr_native_value = None
        else:
            self._attr_native_value = self.get_data()["value"]

        if self.get_data()["type"] == 6:
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif self.get_data()["type"] == 8:
            self._attr_device_class = SensorDeviceClass.POWER
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif self.get_data()["type"] == 4:
            self._attr_device_class = SensorDeviceClass.DURATION
            self._attr_state_class = SensorStateClass.MEASUREMENT
        else:
            self._attr_device_class = None
            self._attr_state_class = None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.get_data()["type"] == 6 or self.get_data()["type"] == 8:
            try:
                self._attr_native_value = float(self.get_data()["value"])
            except TypeError:
                self._attr_native_value = None
            except ValueError:
                self._attr_native_value = None
        else:
            self._attr_native_value = self.get_data()["value"]
        self.async_write_ha_state()

    def get_data(self):
        return self.coordinator.data[self.path]
