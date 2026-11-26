# Get Database

docker compose cp signaldeck:/app/backup/backup.sqlite backup.sqlite

## HTTP input

Ecowitt extends the generic HttpReceiver. Existing sensors, exports, persistence and /http endpoints are unchanged; GET query and POST form/JSON reports are supported. Sensor mappings are generated automatically; missing or invalid readings are omitted from the stored record while the last known sensor value remains available in the UI and ValueProvider. Derived values are calculated only from readings in the same report. By default date is the local reception time, as before. Optionally configure `timestamp_mapping` with name=date, type=date and jsonPath (for example $.dateutc), date_format and timezone matching the actual gateway payload. The configured timestamp must be present and valid. This plugin requires Main >=0.6.3 and SDK >=0.6.4.
