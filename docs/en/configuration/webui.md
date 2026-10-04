# WebUI

Open `http://HOST:8000/` to view service status and manage supported settings.
The WebUI is a same-origin Vue application served by FastAPI from the existing
container.

## Available sections

| Section           | Purpose                                                          |
| ----------------- | ---------------------------------------------------------------- |
| Dashboard         | Database, updater, result-processing, and cached Prowlarr status |
| Database updates  | Enable updates and set the interval                              |
| Result processing | Select a preset or edit custom rules                             |
| Prowlarr          | Save connection details, test access, and add the indexer        |

Changes are persisted to `/data/state/settings.json`. The UI never reads a saved
Prowlarr API key back: it receives only `api_key_configured`.

::: tip Environment-controlled values

Environment variables have higher precedence than persisted settings. A value
controlled by the runtime can appear effective in the UI without being written
to `settings.json`.

:::

## Network posture

The WebUI and its `/webapi` backend have no authentication. Expose them only on
a trusted network or behind an authenticated reverse proxy.
