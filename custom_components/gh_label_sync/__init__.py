from __future__ import annotations

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import entity_registry as er, area_registry as ar, device_registry as dr
from homeassistant.helpers import label_registry as lr  # HA >= 2024.4
from homeassistant.const import Platform

from .const import (
    DOMAIN, CONF_LABEL, CONF_MAP_AREAS,
    CONF_NOTIFY, CONF_AUTOREBUILD, CONF_BROWSER_POPUP,
    DEFAULT_LABEL, OUTFILE, PLATFORMS
)

import os, traceback

def _get_label_id(label):
    return getattr(label, "label_id", getattr(label, "id", None))


async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry

    async def handle_rebuild(call: ServiceCall):
        label = entry.options.get(CONF_LABEL, entry.data.get(CONF_LABEL, DEFAULT_LABEL))
        map_areas = entry.options.get(CONF_MAP_AREAS, entry.data.get(CONF_MAP_AREAS, True))
        notify_on = entry.options.get(CONF_NOTIFY, entry.data.get(CONF_NOTIFY, True))
        use_popup = entry.options.get(CONF_BROWSER_POPUP, entry.data.get(CONF_BROWSER_POPUP, True))

        try:
            count, matched, path = await _rebuild(hass, label, map_areas)
            msg = (
                f"Konfiguration geschrieben (**{count}** Entities)\n"
                f"Datei: `{path}`\n"
                f"Label: `{label}`\n"
                f"Treffer: Entities **{matched['entity']}**, Devices **{matched['device']}**\n"
                "Starte Google Home Label Sync: Knopf *GH LabelSync: Request Sync*."
            )
        except Exception as e:
            msg = f"Fehler beim Rebuild: {e}\n{traceback.format_exc()}"

        if notify_on:
            await _notify(hass, "Google Home Label Sync", msg, use_popup)

    # Auto-Rebuild-Listener
    unsub = None

    async def _on_label_update(event):
        # Event-Name kann je nach HA Version variieren, daher defensiv prüfen
        data = event.data or {}
        # Versuche an den Namen zu kommen (create/update/remove liefern i.d.R. name/label_id)
        changed_name = (data.get("name") or data.get("label", {}).get("name") or "").strip().lower()

        desired_name = (entry.options.get(CONF_LABEL, entry.data.get(CONF_LABEL, DEFAULT_LABEL)) or "").strip().lower()
        auto_on = entry.options.get(CONF_AUTOREBUILD, entry.data.get(CONF_AUTOREBUILD, False))
        if not auto_on:
            return
        if changed_name and changed_name != desired_name:
            return

        # Trifft unser Ziel-Label → Rebuild
        await handle_rebuild(ServiceCall(DOMAIN, "rebuild", {}))

    # Versuche bekannte Events zu abonnieren
    def _attach_listeners():
        listeners = []
        for ev in ("label_registry_updated", "labels_updated"):  # konservativ: beide Varianten
            listeners.append(hass.bus.async_listen(ev, _on_label_update))
        return listeners

    listeners = _attach_listeners()

    async def _async_unsub_listeners(*_):
        for l in listeners:
            try: l()
            except Exception: pass

    entry.async_on_unload(_async_unsub_listeners)        

    async def handle_debug(call: ServiceCall):
        try:
            path = hass.config.path(OUTFILE)
            ent_reg = er.async_get(hass)
            dev_reg = dr.async_get(hass)
            lab_reg = lr.async_get(hass)
            area_reg = ar.async_get(hass)

            labels_list = ", ".join(sorted([l.name for l in lab_reg.labels.values()]))
            testfile = hass.config.path("gh_label_sync_debug_write.test")
            def _write():
                with open(testfile, "w", encoding="utf-8") as f:
                    f.write("ok")
            await hass.async_add_executor_job(_write)

            msg = (
                f"CONFIG PATH: {hass.config.path('.')}\n"
                f"OUTFILE PATH: {path}\n"
                f"Labels im System: {labels_list or '(keine)'}\n"
                f"Entities: {len(ent_reg.entities)} | Devices: {len(dev_reg.devices)}\n"
                f"Testwrite: OK → {testfile}\n"
                "Wenn OUTFILE nicht entsteht, prüfen: Integration geladen? Button sichtbar? Logs?"
            )
        except Exception as e:
            msg = f"DEBUG-Fehler: {e}\n{traceback.format_exc()}"
        await hass.services.async_call(
            "persistent_notification",
            "create",
            {"title": "Google Home Label Sync – Debug", "message": msg, "notification_id": "gh_label_sync_debug"},
        )

    hass.services.async_register(DOMAIN, "rebuild", handle_rebuild)
    hass.services.async_register(DOMAIN, "debug", handle_debug)

    await hass.config_entries.async_forward_entry_setups(entry, [Platform.BUTTON, Platform.SWITCH])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, [Platform.BUTTON, Platform.SWITCH])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok

async def _rebuild(hass: HomeAssistant, label_name: str, map_areas: bool):
    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)
    lab_reg = lr.async_get(hass)
    area_reg = ar.async_get(hass)

    target_label = next((l for l in lab_reg.labels.values()
                        if (l.name or "").strip().lower() == (label_name or "").strip().lower()), None)    
    target_label_id = _get_label_id(target_label) if target_label else None
    
    lines = ["# generated by gh_label_sync"]
    written = 0
    matched_counts = {"entity": 0, "device": 0}

    if not target_label:
        lines.append(f"# Label nicht gefunden: {label_name}")
        content = "\n".join(lines) + "\n"
        out_path = await _write(hass, content)
        return written, matched_counts, out_path

    device_has_label = set()
    for dev in dev_reg.devices.values():
        if target_label_id in (dev.labels or set()):
            device_has_label.add(dev.id)
    matched_counts["device"] = len(device_has_label)

    for entity in sorted(ent_reg.entities.values(), key=lambda e: e.entity_id):
        if not entity.entity_id:
            continue

        has_entity_label = target_label_id in (entity.labels or set())
        if has_entity_label:
            matched_counts["entity"] += 1

        has_device_label = entity.device_id in device_has_label if entity.device_id else False

        if not (has_entity_label or has_device_label):
            continue

        lines.append(f"{entity.entity_id}:")
        lines.append("  expose: true")

        if map_areas:
            area = None
            if entity.area_id:
                area = area_reg.areas.get(entity.area_id)
            else:
                dev = dev_reg.devices.get(entity.device_id) if entity.device_id else None
                if dev and dev.area_id:
                    area = area_reg.areas.get(dev.area_id)
            if area:
                lines.append(f"  room: {area.name}")
        written += 1

    lines.append("")
    content = "\n".join(lines)
    out_path = await _write(hass, content)
    return written, matched_counts, out_path

async def _write(hass: HomeAssistant, content: str):
    out_path = hass.config.path(OUTFILE)

    def _do_write():
        if os.path.exists(out_path):
            try:
                os.replace(out_path, out_path + ".bak")
            except Exception:
                pass
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content if content.endswith("\n") else content + "\n")

    await hass.async_add_executor_job(_do_write)
    return out_path

async def _notify(hass, title, message, use_popup: bool):
    # Versuche echten Popup mit browser_mod
    if use_popup and hass.services.has_service("browser_mod", "popup"):
        await hass.services.async_call("browser_mod", "popup", {
            "title": title,
            "content": {"type": "markdown", "content": message},
            "timeout": 8000,      # ms; schließt automatisch
            "right_button": "OK"
        }, blocking=False)
        return
    # Fallback: persistente Notification
    await hass.services.async_call("persistent_notification", "create", {
        "title": title,
        "message": message,
        "notification_id": "gh_label_sync_info",
    }, blocking=False)