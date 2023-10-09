"""Config flow for KNV heatpump integration."""

# pylint: disable=no-member
# pylint: disable=arguments-renamed

import voluptuous as vol

from homeassistant import config_entries
from . import const as knv

DESCR = "suggested_value"


class KnvHeatpumpFlow(config_entries.ConfigFlow, domain=knv.DOMAIN):
    """
    KNV heatpump config flow
    """

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

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
                    description={
                        DESCR: self.config_entry.options.get(knv.CONF_IP)
                    }
                ): str,
                vol.Required(
                    knv.CONF_USER,
                    description={
                        DESCR: self.config_entry.options.get(knv.CONF_USER)
                    }
                ): str,
                vol.Required(
                    knv.CONF_PASSWORD,
                    description={
                        DESCR: self.config_entry.options.get(knv.CONF_PASSWORD)
                    }
                ): str
            }),
            errors=errors
        )
