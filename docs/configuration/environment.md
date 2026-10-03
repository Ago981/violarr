# Environment variables

Defaults are loaded first, persisted settings second, and runtime environment
overrides last. Runtime overrides are effective without rewriting
`/data/state/settings.json`.

## User-facing overrides

| Variable                 | Default                        | Effect                                                               |
| ------------------------ | ------------------------------ | -------------------------------------------------------------------- |
| `DB_AUTO_UPDATE`         | `true`                         | Overrides automatic-update enabled state                             |
| `DB_UPDATE_INTERVAL`     | `86400`                        | Overrides interval in seconds; valid range 60–604800                 |
| `DB_UPDATE_START_DELAY`  | `60`                           | Delay before the first periodic check                                |
| `ICVDB_RESULT_PRESET`    | `unfiltered`                   | Overrides the active preset                                          |
| `ICVDB_PROWLARR_URL`     | empty                          | Overrides the Prowlarr base URL                                      |
| `ICVDB_PROWLARR_API_KEY` | empty                          | Overrides the Prowlarr API key                                       |
| `PROWLARR_API_KEY`       | empty                          | Compatibility API-key override; wins when both key variables are set |
| `PROWLARR_INDEXER_URL`   | empty                          | Overrides the Torznab URL given to Prowlarr                          |
| `SNAPSHOT_LATEST_URL`    | GitHub latest-release API      | Changes the snapshot release metadata source                         |
| `SNAPSHOT_STATE_FILE`    | `/data/state/snapshot-version` | Changes the installed-version state path                             |
| `ICVDB_SETTINGS_PATH`    | `/data/state/settings.json`    | Changes the settings path                                            |

## Internal runtime variables

The image supplies these values for its embedded PostgreSQL instance. Normal
single-container deployments should not change them.

| Variable            | Image value                     |
| ------------------- | ------------------------------- |
| `DB_HOST`           | `127.0.0.1`                     |
| `DB_PORT`           | `5432`                          |
| `DB_NAME`           | `icv_db`                        |
| `DB_USER`           | `icv`                           |
| `DB_PASSWORD`       | internal container value        |
| `DB_ADMIN_DB`       | `postgres` when unset           |
| `FRONTEND_DIST_DIR` | `/app/frontend-dist` when unset |

::: warning Secrets Use container secrets or protected deployment configuration
for API keys. The application masks keys in normal read responses, but it does
not encrypt values stored in `settings.json`. :::
