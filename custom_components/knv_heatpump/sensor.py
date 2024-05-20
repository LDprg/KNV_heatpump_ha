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
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)


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
        
        LOGGER.warn("listerner called")
        
        if not data["path"] in coordinator.paths:
            if knv.getType(data) == knv.Type.SENSOR:
                coordinator.paths.append(data["path"])
                
                async_add_entities(
                    KnvSensor(coordinator, len(coordinator.paths), data)
                )

    coordinator.async_add_listener(_async_measurement_listener)

class KnvSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, idx, data):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=idx)
        self.idx: int = idx
        self.data: Any = data

        self.name = self.data["path"] + " - " + self.data["name"]
        self.unique_id = self.data["path"]
        
        if self.data["unit"]:
            self.native_unit_of_measurement = self.data["unit"]

        if self.data["type"] == 6 or self.data["type"] == 8:
            try:
                self.native_value = float(self.data["value"])
            except TypeError:
                self.native_value = None
            except ValueError:
                self.native_value = None
        else:
            self.native_value = self.data["value"]

        if self.data["type"] == 6:
            self.device_class = SensorDeviceClass.TEMPERATURE
            self.state_class = SensorStateClass.MEASUREMENT
        elif self.data["type"] == 8:
            self.device_class = SensorDeviceClass.ENERGY_STORAGE
            self.state_class = SensorStateClass.MEASUREMENT
        elif self.data["type"] == 4:
            self.device_class = SensorDeviceClass.DURATION
            self.state_class = SensorStateClass.MEASUREMENT
        else:
            self.device_class = None
            self.state_class = None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if self.coordinator.data["path"] == self.data["path"]:
            self.data["value"] = self.coordinator.data["value"]

            if self.data["type"] == 6 or self.data["type"] == 8:
                try:
                    self.native_value = float(self.data["value"])
                except TypeError:
                    self.native_value = None
                except ValueError:
                    self.native_value = None
            else:
                self.native_value = self.data["value"]

            self.coordinator.logger.info(self.name)

            self.async_write_ha_state()

