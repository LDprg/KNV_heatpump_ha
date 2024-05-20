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

from .coordinator import KNVCoordinator

from . import const as knv


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Setup up a config entry."""
    config = config_entry.data
    coordinator = KNVCoordinator(hass, config)

    await coordinator.async_config_entry_first_refresh()

    hass.data[knv.DOMAIN] = {
        "coord": coordinator
    }

    await asyncio.sleep(1)

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(
            config_entry, ["sensor", "number", "select"])
    )

    return True
