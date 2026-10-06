# Environment variables

Violarr loads configuration in this order:

1. application defaults;
2. persisted settings saved through the WebUI;
3. explicit runtime environment overrides.

Environment variables therefore take precedence over persisted settings, but
they are treated as overrides only when they are explicitly defined by the user.

## User-facing overrides

| Variable                 | Application default            | Effect                                                               |
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

`DB_AUTO_UPDATE` and `DB_UPDATE_INTERVAL` normally do not need to be specified
on the container. This allows values configured through the WebUI to be stored
in `/data/state/settings.json` and applied immediately to the updater.

When either variable is explicitly supplied, its value becomes a runtime
override and takes precedence over the persisted configuration.

For example:

```yaml
environment:
  DB_UPDATE_INTERVAL: '3600'
```

forces a one-hour interval even if a different value is selected through the
WebUI.

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

::: warning Secrets

Use container secrets or protected deployment configuration for API keys. The
application masks keys in normal read responses, but it does not encrypt values
stored in `settings.json`.

:::
