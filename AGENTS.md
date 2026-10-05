# AGENTS.md

## Project overview

Violarr is a lightweight bridge between a local ICVDB PostgreSQL database and Torznab-compatible clients such as Prowlarr. Its public repository is `xbit18/violarr`, and its primary image is `ghcr.io/xbit18/violarr`.

The application:

1. receives Torznab API requests;
2. queries the local PostgreSQL database containing an ICVDB snapshot;
3. converts database records into Torznab-compatible XML;
4. returns the result to the client.

The project does not scrape websites, download torrents, manage media libraries, or maintain the upstream ICVDB database.

## Tech stack

- Python 3.12
- FastAPI
- psycopg 3
- Uvicorn
- PostgreSQL 16
- Docker / Docker Compose

The project is intentionally small. Most application logic currently lives in `app.py`.

## Public identity and compatibility

Use **Violarr** for public product naming and `ghcr.io/xbit18/violarr` as the published image.

The following legacy technical identifiers are intentional compatibility contracts and must not be renamed during branding work:

- Compose service and container alias `icvdb-torznab`;
- named volume `icvdb_torznab_data` and container path `/data`;
- settings path `/data/state/settings.json` and schema version 1;
- `ICVDB_*` and `DB_*` environment variables;
- `/api` and `/webapi` routes;
- snapshot repository `xbit18/icvdb-snapshots`.

## Important files

- `app.py` — API, search logic, database queries and Torznab XML generation
- `Dockerfile` — application container
- `docker-compose.yml` — PostgreSQL + Torznab service deployment
- `.env.example` — supported configuration variables
- `requirements.txt` — Python dependencies
- `README.md` — user-facing installation and usage documentation
- `ARCHITECTURE.md` — architecture and protocol notes
- `AGENTS.md` — instructions for coding agents working on this repository

## Configuration

The Docker Compose deployment uses:

```text
DB_NAME
DB_USER
DB_PASSWORD
```

Inside the Violarr container, database connectivity is configured as:

```text
DB_HOST=db
DB_PORT=5432
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
```

`app.py` also supports database configuration through:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

Never hard-code:

- passwords
- API keys
- tokens
- private IP addresses
- machine-specific paths
- other secrets

Never commit `.env`.

## Running the project

Create the local configuration:

```bash
cp .env.example .env
```

Start PostgreSQL:

```bash
docker compose up -d db
```

Start or rebuild the complete stack:

```bash
docker compose up -d --build
```

View logs:

```bash
docker compose logs -f
```

Stop the stack:

```bash
docker compose down
```

Do not use `docker compose down -v` unless destroying the local PostgreSQL database is explicitly intended.

## Database snapshot

The repository does not contain the ICVDB database itself.

Database snapshots are distributed separately through GitHub Releases because the dump is too large to store directly in the Git repository.

The currently documented snapshot is:

```text
Tag: db-2026-08-21
File: icvdb-2026-08-21.dump
Format: PostgreSQL custom dump
```

The dump is restored into the PostgreSQL service managed by `docker-compose.yml`.

The persistent PostgreSQL data is stored in the Docker volume:

```text
icvdb_data
```

The database should generally be treated as read-only by the Torznab service.

## Restoring a snapshot

After starting the database service, a snapshot can be restored with:

```bash
docker compose exec -T db \
  sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-privileges' \
  < db/icvdb-2026-08-21.dump
```

Do not automatically drop, recreate or overwrite an existing user database unless that behavior has been explicitly requested.

Database replacement and snapshot updates must be designed carefully to avoid unnecessary downtime or accidental data loss.

## Basic verification

After making changes, always verify:

```bash
curl 'http://localhost:8000/api?t=caps'
```

Expected:

- HTTP 200
- valid XML
- root element `<caps>`
- advertised capabilities consistent with the implementation

The capabilities endpoint alone does not verify PostgreSQL connectivity.

Also perform at least one real search:

```bash
curl -s 'http://localhost:8000/api?t=search&q=avatar'
```

When changing movie or TV search logic, test the relevant endpoint as well.

Examples:

```text
/api?t=search&q=example
/api?t=movie&q=example
/api?t=tvsearch&q=example
```

## Torznab compatibility

The main API endpoint is:

```text
/api
```

Currently supported operations include:

- `t=caps`
- `t=search`
- `t=movie`
- `t=tvsearch`

Current categories:

- `2000` — Movies
- `5000` — TV
- `5070` — TV / Anime

When changing the API:

- preserve Torznab compatibility;
- preserve existing query parameters when possible;
- prioritize compatibility with Prowlarr;
- keep `/api?t=caps` synchronized with actual implemented features;
- do not advertise capabilities that are not implemented.

## Database rules

Treat the ICVDB schema as an external data model.

Prefer read-only SQL.

Do not modify the ICVDB schema or introduce application-specific migrations unless explicitly requested.

All HTTP-provided values used in SQL must use psycopg parameter binding.

Never construct SQL by concatenating untrusted request values.

Keep ICVDB-specific schema assumptions easy to locate and understand.

## XML generation

Torznab responses must remain valid XML.

Use the existing `xml.etree.ElementTree` based implementation rather than constructing XML manually through string concatenation.

Database values and user-controlled input must be escaped correctly.

## Security

Treat every HTTP query parameter as untrusted.

Do not expose:

- database credentials;
- internal connection details;
- secrets;
- stack traces containing sensitive information.

Secrets must come from configuration/environment variables.

PostgreSQL should remain internal to the Docker Compose network unless there is a concrete reason to expose it.

## Design principles

Keep the project simple.

Prefer:

- small functions;
- explicit behavior;
- minimal dependencies;
- centralized normalization logic;
- parameterized SQL;
- stateless request handling.

Avoid unnecessary abstractions or frameworks.

The application should remain a thin adapter:

```text
Torznab request
      ↓
input normalization
      ↓
ICVDB query
      ↓
result mapping
      ↓
Torznab XML
```

## Project scope

Appropriate features include:

- improved Torznab compatibility;
- additional Torznab parameters;
- improved ICVDB metadata mapping;
- better error handling;
- logging;
- tests;
- health checks;
- Docker/deployment improvements;
- safer snapshot restoration;
- automated database snapshot retrieval and updating.

Out of scope unless explicitly requested:

- torrent downloading;
- media management;
- torrent website scraping;
- replacing Prowlarr;
- maintaining the upstream ICVDB database.

## Database snapshot distribution

The current project already supports self-hosting using a manually downloaded database snapshot.

Current flow:

```text
GitHub Release
      ↓
download PostgreSQL dump
      ↓
restore into local PostgreSQL
      ↓
Violarr
      ↓
Prowlarr
```

A future goal is automated snapshot discovery and updating.

The intended future model is:

```text
ICVDB database
      ↓
periodic pg_dump
      ↓
static storage
      ├── latest.json
      └── versioned database dump
              ↓
        self-hosted instances
```

A possible manifest format:

```json
{
  "version": "2026-10-08",
  "url": "https://example.org/icvdb/icvdb-2026-10-08.dump",
  "sha256": "..."
}
```

A self-hosted instance could periodically check the manifest and download a new dump only when `version` changes.

Automatic snapshot discovery and updating are not implemented yet.

Do not assume that a stable manifest URL exists unless it has actually been added to the project.

## Documentation

When changing user-visible behavior, update `README.md`.

When changing architecture, database assumptions, Torznab mappings or snapshot/update behavior, update `ARCHITECTURE.md`.

Keep examples generic.

Never put local credentials, private IP addresses or machine-specific configuration into documentation.

## Before finishing a change

Verify that:

1. the Docker image builds;
2. PostgreSQL starts successfully;
3. the Torznab service starts successfully;
4. `/api?t=caps` returns valid XML;
5. at least one real search reaches PostgreSQL successfully;
6. affected search endpoints behave correctly;
7. no credentials or local-only configuration were committed;
8. database dumps were not accidentally committed;
9. documentation reflects user-visible changes.
