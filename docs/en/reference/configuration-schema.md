# Configuration schema

Settings schema version 1 is stored atomically at `/data/state/settings.json`.

## Shape

```json
{
  "schema_version": 1,
  "database_update": {
    "enabled": true,
    "interval_seconds": 86400
  },
  "result_processing": {
    "preset": "unfiltered",
    "custom_rules": []
  },
  "prowlarr": {
    "url": "",
    "indexer_url": "",
    "api_key": ""
  }
}
```

Read responses replace `api_key` with the boolean `api_key_configured`.

## Precedence

```text
built-in defaults < persisted settings < runtime environment overrides
```

Saving from the WebUI starts from persisted values, preventing effective
environment overrides from being copied to disk.

## Validation

- The document has exactly the four top-level fields shown above.
- `schema_version` is exactly numeric `1`.
- Update interval is an integer from 60 through 604800 seconds.
- Preset is `unfiltered`, `italian_preferred`, `italian_only`, or `custom`.
- Prowlarr URLs are empty or absolute HTTP(S) URLs without credentials.
- API keys are strings no longer than 4096 characters.
- Custom rules follow the [bounded rule contract](../features/custom-filters).

## Secret update semantics

For `PUT /webapi/settings`:

- omit `api_key` to preserve the persisted secret;
- send a non-empty `api_key` to replace it;
- send an empty `api_key` to clear it.

An environment-provided key can remain effective after clearing the persisted
key because environment overrides have higher precedence.
