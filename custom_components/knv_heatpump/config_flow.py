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
    async def async_step_user(self, info):
        """
        Init step
        """

        errors = {}

        if info is not None:
            pass

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(
                    knv.CONF_IP,
                    description=knv.CONF_IP
                ): str,
                vol.Required(
                    knv.CONF_USER,
                    description=knv.CONF_USER
                ): str,
                vol.Required(
                    knv.CONF_PASSWORD,
                    description=knv.CONF_PASSWORD
                ): str
            }),
            errors=errors
        )
