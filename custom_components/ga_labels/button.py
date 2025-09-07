
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import Platform
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
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, "ga_labels")}, name="GA Labels")

class GaLabelsRebuildButton(_BaseGaButton):
    _attr_name = "GA Labels: Rebuild"
    _attr_unique_id = "ga_labels_rebuild_button"
    _attr_icon = "mdi:refresh"

    async def async_press(self) -> None:
        await self.hass.services.async_call(DOMAIN, "rebuild", {})

class GaLabelsRequestSyncButton(_BaseGaButton):
    _attr_name = "GA Labels: Request Sync"
    _attr_unique_id = "ga_labels_request_sync_button"
    _attr_icon = "mdi:sync"

    async def async_press(self) -> None:
        # Requires google_assistant manual integration available
        await self.hass.services.async_call("google_assistant", "request_sync", {})
