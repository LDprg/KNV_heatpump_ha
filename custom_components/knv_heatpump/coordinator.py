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
        self.config = config
        self.socket = knvheatpump.Socket()
        self.data = None
        self.paths = []

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

