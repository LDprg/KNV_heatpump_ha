"""Config flow for KNV heatpump integration."""

# pylint: disable=no-member
# pylint: disable=arguments-renamed

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_ERROR, CONF_PASSWORD, CONF_USERNAME, CONF_IP_ADDRESS
from homeassistant.data_entry_flow import AbortFlow

from getmac import get_mac_address

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
            mac = get_mac_address(
                ip=info[CONF_IP_ADDRESS], network_request=True)

            if mac is not None:
                if await self.async_set_unique_id(mac + info[CONF_USERNAME]):
                    raise AbortFlow("already_configured")
                return self.async_create_entry(
                    title="test",
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
