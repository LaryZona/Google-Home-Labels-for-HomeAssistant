from __future__ import annotations
from .const import DOMAIN, CONF_MAP_AREAS, CONF_NOTIFY, CONF_AUTOREBUILD, CONF_BROWSER_POPUP

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_MAP_AREAS

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([
        GaLabelsMapAreasSwitch(hass, entry),
        GaLabelsNotifySwitch(hass, entry),        
        GaLabelsAutoRebuildSwitch(hass, entry),   
        GaLabelsBrowserPopupSwitch(hass, entry),  
    ])

class GaLabelsMapAreasSwitch(SwitchEntity):
    _attr_name = "Google Home Label Sync: Map Areas → Rooms"
    _attr_unique_id = "gh_label_sync_map_areas_switch"
    _attr_icon = "mdi:home-floor-l"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self._entry = entry
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, "gh_label_sync")}, name="Google Home Label Sync")

    @property
    def is_on(self): return self._get(CONF_MAP_AREAS, True)
    async def async_turn_on(self, **_): self._set(CONF_MAP_AREAS, True)
    async def async_turn_off(self, **_): self._set(CONF_MAP_AREAS, False)

class _BaseSwitch(SwitchEntity):
    def __init__(self, hass, entry):
        self.hass = hass
        self._entry = entry
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, "gh_label_sync")}, name="Google Home Label Sync")

    def _get(self, key, default):
        return self._entry.options.get(key, self._entry.data.get(key, default))

    def _set(self, key, value):
        opts = dict(self._entry.options)
        opts[key] = value
        self.hass.config_entries.async_update_entry(self._entry, options=opts)
        self.async_write_ha_state()


class GaLabelsNotifySwitch(_BaseSwitch):
    _attr_name = "Google Home Label Sync: Debug/Notifications"
    _attr_unique_id = "gh_label_sync_notify_switch"
    _attr_icon = "mdi:bell"

    @property
    def is_on(self): return self._get(CONF_NOTIFY, True)
    async def async_turn_on(self, **_): self._set(CONF_NOTIFY, True)
    async def async_turn_off(self, **_): self._set(CONF_NOTIFY, False)

class GaLabelsAutoRebuildSwitch(_BaseSwitch):
    _attr_name = "Google Home Label Sync: Auto-Rebuild bei Label-Änderungen"
    _attr_unique_id = "gh_label_sync_auto_rebuild_switch"
    _attr_icon = "mdi:autorenew"

    @property
    def is_on(self): return self._get(CONF_AUTOREBUILD, False)
    async def async_turn_on(self, **_): self._set(CONF_AUTOREBUILD, True)
    async def async_turn_off(self, **_): self._set(CONF_AUTOREBUILD, False)

class GaLabelsBrowserPopupSwitch(_BaseSwitch):
    _attr_name = "Google Home Label Sync: Popup via browser_mod"
    _attr_unique_id = "gh_label_sync_browser_popup_switch"
    _attr_icon = "mdi:arrow-expand-all"

    @property
    def is_on(self): return self._get(CONF_BROWSER_POPUP, True)
    async def async_turn_on(self, **_): self._set(CONF_BROWSER_POPUP, True)
    async def async_turn_off(self, **_): self._set(CONF_BROWSER_POPUP, False)