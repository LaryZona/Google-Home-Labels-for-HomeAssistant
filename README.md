# ha-google-assistant-label-sync

!Work in Progress!

This HomeAssistant HACS Add-on works for the HomeAssistant integration into the Google Home App (Google Cloud Console). It simplifies the process of filtering exported devices by tagging them with Labels.


Expose Home Assistant Entities to Google Assistant **per Label**.  
Mark your devices/entities with the label **"Google Home"** (or any label you configure) and only those will be exported to Google Assistant.

Optional: Map Home Assistant **Areas → Google Assistant Rooms** automatically.

---

## Features
- Expose entities to Google Assistant by label (default: `Google Home`)
- Optional: map HA Areas directly to Google Assistant `room:` fields
- Service: `ga_labels.rebuild` regenerates the YAML
- Entities:
  - **Button: GA Labels – Rebuild** → writes `google_assistant.entity_config.yaml`
  - **Button: GA Labels – Request Sync** → calls `google_assistant.request_sync`
  - **Switch: GA Labels – Map Areas → Rooms** → toggle automatic room mapping
- Creates a `.bak` backup if `google_assistant.entity_config.yaml` already exists

---

## Installation (via HACS)
1. Open **HACS → Integrations → Custom repositories**.
2. Add this repo URL, category = **Integration**.
3. Install **GA Labels**.
4. Restart Home Assistant.
5. Go to **Settings → Devices & Services → Add Integration → GA Labels**.

---

## One-time configuration in `configuration.yaml`
Add this block to your `configuration.yaml`:

```yaml
google_assistant:
  project_id: YOUR_PROJECT_ID
  service_account: !include SERVICE_ACCOUNT.json
  report_state: true
  expose_by_default: false
  entity_config: !include google_assistant.entity_config.yaml
```

> ⚠️ This integration is meant for the manual Google Assistant setup (via Google Cloud / Actions SDK).
It does not modify Nabu Casa Cloud settings.




---

Usage

1. In Home Assistant, assign the label Google Home (or your configured label) to any entity or device you want to expose.


2. Press GA Labels: Rebuild → generates/updates google_assistant.entity_config.yaml.


3. Restart Home Assistant (GA YAML is loaded only at startup).


4. Press GA Labels: Request Sync → pushes changes to Google Assistant.


5. (Optional) Toggle GA Labels: Map Areas → Rooms switch to automatically assign Google Assistant rooms from HA areas.




---

Example workflow

Label a light with Google Home and assign it to area Living Room.

Run Rebuild → YAML entry will look like:

entity_config:
  light.livingroom_ceiling:
    expose: true
    room: Living Room

Restart HA → Press Request Sync → The light appears in Google Home, already in the correct room.



---

Notes

Requires Home Assistant 2024.4+ (for label registry support).

Aliases and custom names are not managed here – you can set them directly in the Google Home app.

File is generated at config/google_assistant.entity_config.yaml with a .bak backup.
