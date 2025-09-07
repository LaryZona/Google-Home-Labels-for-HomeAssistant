from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    async_add_entities([
        GaLabelsRebuildButton(hass, entry),
        GaLabelsRequestSyncButton(hass, entry),
    ])

class _BaseGaButton(ButtonEntity):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self._entry = entry
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, "gh_label_sync")}, name="Google Home Label Sync")

class GaLabelsRebuildButton(_BaseGaButton):
    _attr_name = "Google Home Label Sync: Rebuild"
    _attr_unique_id = "gh_label_sync_rebuild_button"
    _attr_icon = "mdi:refresh"

    async def async_press(self) -> None:
        await self.hass.services.async_call(DOMAIN, "rebuild", {})

class GaLabelsRequestSyncButton(_BaseGaButton):
    _attr_name = "Google Home Label Sync: Request Sync"
    _attr_unique_id = "gh_label_sync_request_sync_button"
    _attr_icon = "mdi:sync"

    async def async_press(self) -> None:
        await self.hass.services.async_call("google_assistant", "request_sync", {})
