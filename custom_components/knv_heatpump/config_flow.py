"""Config flow for KNV heatpump integration."""

# pylint: disable=no-member
# pylint: disable=arguments-renamed

from __future__ import annotations

import voluptuous as vol
import arpreq as arp

from homeassistant import config_entries
from homeassistant.const import CONF_ERROR, CONF_PASSWORD, CONF_USERNAME, CONF_IP_ADDRESS
from homeassistant.data_entry_flow import AbortFlow

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
            mac = arp.arpreq(info[CONF_IP_ADDRESS])

            if mac is not None:
                await self.async_set_unique_id(mac + info[CONF_USERNAME])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    data=info,
                )
            else:
                errors[CONF_ERROR] = knv.ERR_INVALID_IP

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_IP_ADDRESS): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str
            }),
            errors=errors
        )
