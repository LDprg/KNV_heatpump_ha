from __future__ import annotations
import asyncio

from typing import Any

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_IP_ADDRESS
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from knvheatpumplib import knvheatpump

from . import const as knv


class KNVCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, config):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            knv.LOGGER,
            name=knv.DOMAIN,
        )
        self.hass = hass
        self.config = config
        self.socket = knvheatpump.Socket()
        self.paths = []

        self.createSocket()

    def createSocket(self):
        async def callback(data):
            try:
                self.async_set_updated_data(data)
            except Exception as e:
                print(e)

        asyncio.run_coroutine_threadsafe(self.socket.create(
            self.config[CONF_IP_ADDRESS], self.config[CONF_USERNAME], self.config[CONF_PASSWORD], callback), self.hass.loop)
