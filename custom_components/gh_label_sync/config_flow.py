from __future__ import annotations

from homeassistant import config_entries
import voluptuous as vol

from .const import (
    DOMAIN, CONF_LABEL, CONF_MAP_AREAS,
    CONF_NOTIFY, CONF_AUTOREBUILD, CONF_BROWSER_POPUP,
    DEFAULT_LABEL
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Google Home Label Sync", data=user_input)

        schema = vol.Schema({
            vol.Optional(CONF_LABEL, default=DEFAULT_LABEL): str,
            vol.Optional(CONF_MAP_AREAS, default=True): bool,
            vol.Optional(CONF_NOTIFY, default=True): bool,
            vol.Optional(CONF_AUTOREBUILD, default=False): bool,
            vol.Optional(CONF_BROWSER_POPUP, default=True): bool,
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    def async_get_options_flow(entry):
        return OptionsFlowHandler(entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, entry):
        self._entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = self._entry.options or self._entry.data or {}
        schema = vol.Schema({
            vol.Optional(CONF_LABEL, default=data.get(CONF_LABEL, DEFAULT_LABEL)): str,
            vol.Optional(CONF_MAP_AREAS, default=data.get(CONF_MAP_AREAS, True)): bool,
            vol.Optional(CONF_NOTIFY, default=data.get(CONF_NOTIFY, True)): bool,             
            vol.Optional(CONF_AUTOREBUILD, default=data.get(CONF_AUTOREBUILD, False)): bool,  
            vol.Optional(CONF_BROWSER_POPUP, default=data.get(CONF_BROWSER_POPUP, True)): bool 
        })
        return self.async_show_form(step_id="init", data_schema=schema)
