"""
The "hello world" custom component.

This component implements the bare minimum that a component should implement.

Configuration:

To use the hello_world component you will need to add the following to your
configuration.yaml file.

knv_heatpump:
"""

# pylint: disable=no-member

from __future__ import annotations

from datetime import timedelta

import async_timeout

from homeassistant.core import HomeAssistant, callback
from homeassistant.components.light import LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)


from . import const as knv


async def async_setup(_hass: HomeAssistant, _config: ConfigType):
    """Setup our skeleton component."""

    return True


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup up a config entry."""

    # assuming API object stored here by __init__.py
    my_api = hass.data[knv.DOMAIN][entry.entry_id]
    coordinator = MyCoordinator(hass, my_api)

    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        MyEntity(coordinator, idx) for idx, ent in enumerate(coordinator.data)
    )

    return True


class MyCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, my_api):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            knv.LOGGER,
            # Name of the data. For logging purposes.
            name="My sensor",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
        )
        self.my_api = my_api

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        # try:
        # Note: asyncio.TimeoutError and aiohttp.ClientError are already
        # handled by the data update coordinator.
        #    async with async_timeout.timeout(10):
        # Grab active context variables to limit data required to be fetched from API
        # Note: using context is not required if there is no need or ability to limit
        # data retrieved from API.
        #        listening_idx = set(self.async_contexts())
        #        return await self.my_api.fetch_data(listening_idx)
        # except ApiAuthError as err:
        # Raising ConfigEntryAuthFailed will cancel future updates
        # and start a config flow with SOURCE_REAUTH (async_step_reauth)
        #    raise ConfigEntryAuthFailed from err
        # except ApiError as err:
        #    raise UpdateFailed(f"Error communicating with API: {err}")


class MyEntity(CoordinatorEntity, LightEntity):
    """An entity using CoordinatorEntity.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """

    def __init__(self, coordinator, idx):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=idx)
        self.idx = idx

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.data[self.idx]["state"]
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        """Turn the light on.

        Example method how to request data updates.
        """
        # Do the turning on.
        # ...

        # Update the data
        await self.coordinator.async_request_refresh()
