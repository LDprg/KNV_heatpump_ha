"""Config flow for KNV heatpump integration."""

# pylint: disable=no-member
# pylint: disable=arguments-renamed

import voluptuous as vol

from homeassistant import config_entries
from . import const as knv


class KnvHeatpumpFlow(config_entries.ConfigFlow, domain=knv.DOMAIN):
    """
    KNV heatpump config flow
    """
    async def async_step_init(self, info):
        """
        Init step
        """
        if info is not None:
            pass

        return self.async_show_form(
            step_id="init", data_schema=vol.Schema({vol.Required("host"): str})
        )
