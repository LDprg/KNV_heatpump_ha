"""
The "hello world" custom component.

This component implements the bare minimum that a component should implement.

Configuration:

To use the hello_world component you will need to add the following to your
configuration.yaml file.

knv_heatpump:
"""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = "knv_heatpump"


async def async_setup(hass: HomeAssistant, _config: ConfigType):
    """Setup our skeleton component."""

    hass.states.async_set('knv_heatpump.Hello_World', 'Works!')

    return True
