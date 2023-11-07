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
    read = []

    for data in coordinator.data:
        if data["writeable"] is not True or (data["type"] != 6 and data["type"] != 8):
            read.append(data)

    async_add_entities(
        (KnvReadSensor(coordinator, idx, data)
         for idx, data in enumerate(read))
    )


class KnvReadSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, idx, data=None):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=idx)
        self.idx: int = idx
        self.data: Any = data

        if self.data is not None:
            self._attr_name = self.data["path"] + " - " + self.data["name"]
            self._attr_unique_id = self.data["path"]

            if self.data["type"] == 6:
                self._attr_device_class = SensorDeviceClass.TEMPERATURE
                self._attr_state_class = SensorStateClass.MEASUREMENT
            elif self.data["type"] == 8:
                self._attr_device_class = SensorDeviceClass.ENERGY_STORAGE
                self._attr_state_class = SensorStateClass.MEASUREMENT
            else:
                self._attr_device_class = None
                self._attr_state_class = None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if self.coordinator.data["path"] == self.data["path"]:
            self.data["value"] = self.coordinator.data["value"]

            self.coordinator.logger.info(self._attr_name)

            self.async_write_ha_state()

    @property
    def state(self) -> Any:
        if self.data["value"] and self.data["type"]:
            value = self.data["value"]
            types = self.data["type"]

            if types == 6 or types == 8:
                try:
                    return float(value)
                except TypeError:
                    return None
                except ValueError:
                    return None
            else:
                return value
        else:
            return None

    @property
    def unit_of_measurement(self) -> str | None:
        if self.data["unit"]:
            return self.data["unit"]
        else:
            return None
