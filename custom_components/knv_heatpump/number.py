"""Platform for sensor integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
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
    async_add_entities,
) -> None:
    """Setup sensors from a config entry created in the integrations UI."""
    coordinator: KNVCoordinator = hass.data[knv.DOMAIN]["coord"]

    number = []

    for data in coordinator.data:
        if knv.getType(data) == knv.Type.NUMBER:
            number.append(data)

    async_add_entities(
        KnvNumber(coordinator, idx, data) for idx, data in enumerate(number)
    )


class KnvNumber(CoordinatorEntity, NumberEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, idx, data=None):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=idx)
        self.idx: int = idx
        self.data: Any = data

        if self.data is not None:
            self._attr_name = self.data["path"] + " - " + self.data["name"]
            self._attr_unique_id = self.data["path"]

            if "value" in self.data:
                self._attr_native_value = self.data["value"]

            self._attr_native_max_value = float(self.data["max"])
            self._attr_native_min_value = float(self.data["min"])
            self._attr_native_step = float(self.data["step"])
            self._attr_native_unit_of_measurement = self.data["unit"]

            if self.data["type"] == 6:
                self._attr_device_class = NumberDeviceClass.TEMPERATURE
            elif self.data["type"] == 8:
                self._attr_device_class = NumberDeviceClass.ENERGY_STORAGE
            elif self.data["type"] == 4:
                self._attr_device_class = NumberDeviceClass.DURATION

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if self.coordinator.data["path"] == self.data["path"]:
            self.data["value"] = self.coordinator.data["value"]
            self._attr_native_value = self.data["value"]

            self.coordinator.logger.info(self._attr_name)

            self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        if self.date["writeable"] is True:
            await self.coordinator.socket.send(self.data["path"], value)
        else:
            raise NotImplementedError()
