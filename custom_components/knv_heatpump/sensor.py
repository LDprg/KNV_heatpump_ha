"""Platform for sensor integration."""
from __future__ import annotations
import asyncio

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
)
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_IP_ADDRESS
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from knvheatpumplib import knvheatpump

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
    read = []
    write = []

    for data in coordinator.data:
        if data["writeable"] and (data["type"] == 6 or data["type"] == 8):
            write.append(data)
        else:
            read.append(data)

    async_add_entities(
        (KnvReadSensor(coordinator, idx, data)
         for idx, data in enumerate(read)),
        (KnvWriteSensor(coordinator, idx, data)
         for idx, data in enumerate(write))
    )


class KNVCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, config):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            knv.LOGGER,
            # Name of the data. For logging purposes.
            name="KNV",
        )
        self.config = config
        self.socket = knvheatpump.Socket()

        async def callbacks(data):
            try:
                self.async_set_updated_data(data)
            except Exception as e:
                print(e)

        asyncio.run_coroutine_threadsafe(self.socket.create(
            config[CONF_IP_ADDRESS], config[CONF_USERNAME], config[CONF_PASSWORD], callbacks), hass.loop)

    @callback
    def async_set_updated_data(self, data) -> None:
        """Manually update data, notify listeners and reset refresh interval."""
        self._async_unsub_refresh()
        self._debounced_refresh.async_cancel()

        self.data = data
        self.last_update_success = True
        self.logger.debug(
            "Manually updated %s data",
            self.name,
        )

        if self._listeners:
            self._schedule_refresh()

        self.async_update_listeners()

    async def _async_update_data(self):
        data: Any = await knvheatpump.get_data(self.config[CONF_IP_ADDRESS], self.config[CONF_USERNAME], self.config[CONF_PASSWORD])

        array = []
        for val in data:
            array.append(data[val])

        return array


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

    @property
    def unit_of_measurement(self) -> str | None:
        if self.data["unit"]:
            return self.data["unit"]
        else:
            return None


class KnvWriteSensor(CoordinatorEntity, NumberEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, idx, data=None):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=idx)
        self.idx: int = idx
        self.data: Any = data

        if self.data is not None:
            self._attr_name = self.data["path"] + " - " + self.data["name"]
            self._attr_unique_id = self.data["path"]

            self.native_max_value = self.data["max"]
            self.native_min_value = self.data["min"]
            self.native_step = self.data["step"]

            if self.data["type"] == 6:
                self._attr_device_class = NumberDeviceClass.TEMPERATURE
            elif self.data["type"] == 8:
                self._attr_device_class = NumberDeviceClass.ENERGY_STORAGE
            else:
                self._attr_device_class = None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if self.coordinator.data["path"] == self.data["path"]:
            self.data["value"] = self.coordinator.data["value"]

            self.coordinator.logger.info(self._attr_name)

            self.async_write_ha_state()

    @property
    def state(self) -> Any:
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

    @property
    def unit_of_measurement(self) -> str | None:
        if self.data["unit"]:
            return self.data["unit"]
        else:
            return None

    async def async_set_native_value(self, value: float):
        if self.data["writeable"]:
            self.coordinator.socket.send(self.data["path"], value)
