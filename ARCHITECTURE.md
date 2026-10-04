# Architecture

Violarr is a thin, single-container adapter between an ICVDB PostgreSQL
snapshot and Torznab-compatible clients. v1.1 adds a WebUI and persistent
configuration without changing the v1.0 runtime boundary.

## Runtime topology

```text
┌──────────────────────────────────────────────────────────┐
│ Violarr container (operational alias: icvdb-torznab)     │
│                                                          │
│  :8000 FastAPI                                           │
│    ├── /         Vue WebUI                               │
│    ├── /webapi   settings, status, updater, Prowlarr     │
│    └── /api      Torznab XML                             │
│                     │                                    │
│  PostgreSQL 16 ◄────┘  127.0.0.1:5432 only              │
│                                                          │
│  /data                                                   │
│    ├── postgres/                                         │
│    └── state/{settings.json,snapshot-version}            │
└──────────────────────────────────────────────────────────┘
```

Only port `8000` is published. PostgreSQL is not exposed, and the application
does not use a Docker socket, Redis, a separate settings database, or a second
runtime container.

## Modules

| Module | Responsibility |
| --- | --- |
| `app.py` | FastAPI lifecycle, Torznab queries/XML, result-processing integration, static WebUI serving |
| `settings.py` | Schema-v1 validation, atomic persistence, environment precedence, public secret masking |
| `result_processor.py` | Italian presets and bounded custom score/exclusion rules |
| `webapi.py` | Same-origin JSON status, settings, processing, and Prowlarr endpoints |
| `prowlarr.py` | `X-Api-Key` client, Generic Torznab schema derivation, test/create/idempotency |
| `snapshot_updater.py` | Snapshot discovery, validation, candidate restore, switch, rollback, updater state |
| `frontend/` | Vue 3 WebUI source and shared product design tokens |
| `entrypoint.sh` | PostgreSQL bootstrap, first snapshot restore, Uvicorn lifecycle, clean shutdown |

## Image build and startup

The Dockerfile has a Node build stage for `frontend/`. Only generated production
assets are copied into the PostgreSQL/Python runtime at `/app/frontend-dist`.
FastAPI registers `/api` and `/webapi` before low-priority static and SPA fallback
routes. Reserved API, OpenAPI, docs, and ReDoc paths cannot fall through to the
SPA.

Startup preserves the v1.0 sequence:

```text
initialize or reuse /data/postgres
        ↓
start PostgreSQL and wait for readiness
        ↓
create application database when needed
        ↓
bootstrap latest snapshot when no installed state exists
        ↓
start FastAPI and the periodic updater
```

The runtime integration is implemented, but image build, container smoke,
persistence restart, and real v1.0-volume upgrade verification remain pending on
a Docker-capable host.

## Request flows

### Torznab

```text
/api query parameters
        ↓
normalized values and parameterized psycopg SQL
        ↓
optional result processing
        ↓
ElementTree Torznab RSS serialization
```

`t=search`, `t=movie`, and `t=tvsearch` retain the v1.0 parameters, categories,
limits, offset behavior, and XML item shape. The default `unfiltered` preset
passes `limit` and `offset` directly to the database.

### WebUI and WebAPI

```text
browser → Vue static assets → same-origin /webapi
                              ├── settings store
                              ├── updater state/reconfigure
                              ├── database probe
                              └── Prowlarr client
```

The aggregate status endpoint does not make a live Prowlarr request. Live status
is fetched by the focused Prowlarr status endpoint and retained only as an
in-process summary.

### Prowlarr

The client sends `X-Api-Key` to Prowlarr. It reads
`/api/v1/indexer/schema`, selects the Generic Torznab `Torznab` implementation,
deep-clones the schema resource, names it `Violarr`, and fills `baseUrl`,
`apiPath`, and the blank Torznab `apiKey` field. Add checks existing Torznab
resources by normalized origin/path before asking Prowlarr to test and create the
resource, making repeated requests idempotent.

The focused Prowlarr status route reports remote failures in an HTTP `200` status
payload. It preserves secret-safe specific client errors, but replaces any error
containing the configured key or traceback text with `Prowlarr request failed`.
The POST test/create routes return that stable detail with HTTP `502` for remote
failures. API keys and tracebacks are not returned.

## Settings model

Settings use schema version 1 and default to:

- automatic updates enabled every 86400 seconds;
- `unfiltered` result processing with no custom rules;
- empty Prowlarr URL, Indexer URL, and API key.

Effective precedence is:

```text
built-in defaults < /data/state/settings.json < runtime environment
```

`SettingsStore.save` writes a temporary file in the state directory, flushes and
fsyncs it, then replaces `settings.json` atomically. WebUI updates begin from
persisted values so runtime overrides are not accidentally copied to disk.

Public settings replace `api_key` with `api_key_configured`. Omitting the key on
update preserves the stored value, a non-empty value replaces it, and an empty
value clears it. An environment-provided key is effective but never persisted.

Supported settings overrides are `DB_AUTO_UPDATE`, `DB_UPDATE_INTERVAL`,
`ICVDB_RESULT_PRESET`, `ICVDB_PROWLARR_URL`, `ICVDB_PROWLARR_API_KEY`,
`PROWLARR_API_KEY`, and `PROWLARR_INDEXER_URL`. `PROWLARR_API_KEY` wins when both
API-key aliases are set.

## Result pipeline

Rows have the processing fields `title`, `size`, `seeders`, and `provider`.

- `unfiltered` preserves database order.
- `italian_only` keeps exact title tokens `ITA`, `ITALIAN`, or `ITALIANO`.
- `italian_preferred` scores those explicit markers at 100 and exact `MULTI` or
  `DUAL` tokens at 25.
- `custom` removes rows matching enabled exclusion rules, then stably ranks the
  remainder by summed score rules.

Rules are structured and bounded: no regular expressions or scripts, at most
100 rules, text values up to 512 characters, finite numbers, and score magnitude
up to 1000. Text operators compare Unicode case-folded values; null text matches
only `not_contains`. Numeric operators require finite non-boolean values on both
sides, so null and non-finite row values never match.

Processed pagination operates on fixed, non-overlapping 1000-row database
windows. Ranking is local to each window, equal scores preserve original order,
and filtered pages are not backfilled from later windows.

This pipeline affects only ICVDB's XML response. It cannot guarantee downstream
Radarr/Sonarr selection. Hard filters hide results from Prowlarr entirely.

## Snapshot invariants

Snapshot metadata comes from the configured GitHub latest-release endpoint. The
updater selects a `.dump` asset and requires its GitHub `sha256:` digest.

Before switching, it verifies:

1. downloaded SHA256;
2. custom dump readability with `pg_restore --list`;
3. restore completion with `--exit-on-error` into `icv_db_candidate`;
4. candidate connectivity and presence of user tables.

The active `icv_db` remains available during download, inspection, restore, and
candidate validation. Maintenance mode begins only for the database rename and
post-switch validation; HTTP requests then receive `503` with `Retry-After: 5`.

```text
icv_db           → icv_db_previous
icv_db_candidate → icv_db
```

After successful final validation, the updater atomically writes
`/data/state/snapshot-version` and removes the previous database. A failed final
validation attempts rollback from `icv_db_previous`. Earlier failures never
modify the active database.

## Security boundaries

- WebUI, WebAPI, and Torznab currently have no authentication.
- `apikey` is accepted for Torznab compatibility but not validated.
- Deploy port `8000` only on a trusted LAN or behind an authenticated proxy.
- Prowlarr API keys are masked in normal reads and sanitized from WebAPI errors.
- Stored settings are not encrypted; protect the `/data` volume.
- PostgreSQL binds internally to `127.0.0.1:5432`.
- All HTTP-derived SQL values use psycopg parameter binding.
- XML is built with `xml.etree.ElementTree`, not string concatenation.

## Upgrade compatibility

The published image is `ghcr.io/xbit18/violarr`.

v1.1 preserves the v1.0 Compose service and container name `icvdb-torznab`,
named volume `icvdb_torznab_data`, image port, PostgreSQL 16 cluster location,
`/data` volume, `/data/state/settings.json`, schema version 1, `ICVDB_*` and
`DB_*` environment variables, `/api` and `/webapi` routes, snapshot-version
state, snapshot source `xbit18/icvdb-snapshots`, bootstrap/update model, and XML
contract. These legacy technical identifiers intentionally remain stable for
existing volumes, configuration, automation, and Prowlarr URLs. An existing
v1.0 volume should be reused directly; v1.1 adds `settings.json` with defaults
on first access.

Never remove the volume during an application-image upgrade. Full Docker-based
upgrade verification remains a release-readiness task, so this compatibility
claim reflects the preserved implementation invariants rather than a completed
runtime certification.
