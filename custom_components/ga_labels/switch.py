
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_MAP_AREAS

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    async_add_entities([GaLabelsMapAreasSwitch(hass, entry)])

class GaLabelsMapAreasSwitch(SwitchEntity):
    _attr_name = "GA Labels: Map Areas → Rooms"
    _attr_unique_id = "ga_labels_map_areas_switch"
    _attr_icon = "mdi:home-floor-l"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self._entry = entry
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, "ga_labels")}, name="GA Labels")

    @property
    def is_on(self):
        return self._entry.options.get(CONF_MAP_AREAS, self._entry.data.get(CONF_MAP_AREAS, True))

    async def async_turn_on(self, **kwargs):
        opts = dict(self._entry.options)
        opts[CONF_MAP_AREAS] = True
        self.hass.config_entries.async_update_entry(self._entry, options=opts)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        opts = dict(self._entry.options)
        opts[CONF_MAP_AREAS] = False
        self.hass.config_entries.async_update_entry(self._entry, options=opts)
        self.async_write_ha_state()
