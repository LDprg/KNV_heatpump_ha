"""Platform for sensor integration."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_IP_ADDRESS
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from knvheatpumplib import knvheatpump

from . import const as knv


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[knv.DOMAIN][config_entry.entry_id]
    # Update our config
    if config_entry.options:
        config.update(config_entry.options)

    values = await knvheatpump.get_data(
        config[CONF_IP_ADDRESS], config[CONF_USERNAME], config[CONF_PASSWORD])
    async_add_entities([KnvSensor(val) for val in values])


async def async_setup_platform(
    _hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    _discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    values = await knvheatpump.get_data(
        config[CONF_IP_ADDRESS], config[CONF_USERNAME], config[CONF_PASSWORD])
    async_add_entities([KnvSensor(val) for val in values])


class KnvSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, val) -> None:
        """Initialize the sensor."""
        self._state = val["value"]
        self._uid = val["path"]

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._uid

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._uid

    @property
    def state(self) -> str | None:
        """Return the state of the sensor."""
        return self._state
