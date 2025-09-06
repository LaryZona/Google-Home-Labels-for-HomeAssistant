# Google-Home-Labels-for-HomeAssistant
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
