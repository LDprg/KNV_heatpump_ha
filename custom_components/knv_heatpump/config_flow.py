"""Config flow for KNV heatpump integration."""

from homeassistant import config_entries
from . import const as knv


class ExampleConfigFlow(config_entries.ConfigFlow, domain=knv.DOMAIN):
    """Example config flow."""
    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1
