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


from . import const as knv


# async def async_setup(hass: HomeAssistant, _config: ConfigType):
#     """Setup up a config."""

#     return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup up a config entry."""

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor"),
        hass.config_entries.async_forward_entry_setup(entry, "numbers")
    )

    return True
