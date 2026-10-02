# AGENTS.md

## Project overview

`icvdb-torznab` is a lightweight bridge between an ICVDB PostgreSQL database and Torznab-compatible clients such as Prowlarr.

The application:

1. receives Torznab API requests;
2. queries an existing ICVDB PostgreSQL database;
3. converts database records into Torznab-compatible XML;
4. returns the result to the client.

The project does not scrape websites, download torrents, manage media libraries, or populate the ICVDB database.

## Tech stack

- Python 3.12
- FastAPI
- psycopg 3
- Uvicorn
- PostgreSQL
- Docker / Docker Compose

The project is intentionally small. Most application logic currently lives in `app.py`.

## Important files

- `app.py` — API, search logic, database queries and Torznab XML generation
- `Dockerfile` — application container
- `docker-compose.yml` — deployment configuration
- `.env.example` — supported configuration variables
- `requirements.txt` — Python dependencies
- `README.md` — user-facing documentation
- `ARCHITECTURE.md` — architecture and protocol notes

## Configuration

Database configuration must come from environment variables:

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

Build and start:

```bash
docker compose up -d --build
```

Logs:

```bash
docker compose logs -f
```

Stop:

```bash
docker compose down
```

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

When changing search logic, also test the relevant endpoints.

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

## Database

The application currently expects an already populated ICVDB PostgreSQL database.

Treat the ICVDB database as an external dependency.

Prefer read-only SQL.

Do not alter the upstream ICVDB schema or add migrations unless explicitly requested.

All HTTP-provided values used in SQL must use psycopg parameter binding. Never construct SQL by concatenating untrusted values.

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

This application should remain a thin adapter:

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
- automated database snapshot retrieval.

Out of scope unless explicitly requested:

- torrent downloading;
- media management;
- torrent website scraping;
- replacing Prowlarr;
- maintaining the upstream ICVDB database.

## Database snapshot distribution

A future goal is to make the project fully self-hostable without requiring every user to independently obtain an ICVDB database dump.

The intended model is:

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

A possible `latest.json` format:

```json
{
  "version": "2026-10-08",
  "url": "https://example.org/icvdb/icvdb-2026-10-08.dump",
  "sha256": "..."
}
```

A self-hosted instance could periodically check the manifest and download a new dump only when `version` changes.

This feature is NOT implemented yet.

Do not assume that a public dump URL or update service exists unless it has actually been added to the project.

## Documentation

When changing user-visible behavior, update `README.md`.

When changing architecture, database assumptions, Torznab mappings or snapshot/update behavior, update `ARCHITECTURE.md`.

## Before finishing a change

Verify that:

1. the application starts;
2. the Docker image builds;
3. PostgreSQL connectivity still works;
4. `/api?t=caps` returns valid XML;
5. affected search endpoints behave correctly;
6. no credentials or local configuration were committed;
7. documentation reflects user-visible changes.
