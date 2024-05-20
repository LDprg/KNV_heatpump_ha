"""Config flow for KNV heatpump integration."""

# pylint: disable=c-extension-no-member
# pylint: disable=no-member
# pylint: disable=arguments-renamed

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_IP_ADDRESS
from homeassistant.helpers import device_registry

from getmac import get_mac_address

from . import const as knv

ERR_BASE = "base"


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
            knv.LOGGER.info("Gathering mac address")

            try:
                mac = get_mac_address(ip=info[CONF_IP_ADDRESS].strip(), network_request=True)
            except ValueError:
                mac = None

            if mac is not None:
                knv.LOGGER.info("Found mac: %s", mac)

                await self.async_set_unique_id(device_registry.format_mac(mac))
                self._abort_if_unique_id_configured()

                knv.LOGGER.info("Finishing Flow")

                return self.async_create_entry(
                    title="KNV heatpump",
                    data=info,
                )
            else:
                knv.LOGGER.error("Invalid IP")
                errors[ERR_BASE] = knv.ERR_INVALID_IP

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_IP_ADDRESS): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str
            }),
            errors=errors
        )
