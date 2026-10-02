# Architecture

## Purpose

`icvdb-torznab` exposes release information stored in a local PostgreSQL copy of the ICVDB database through a Torznab-compatible API.

Its primary purpose is to allow applications such as Prowlarr to use ICVDB as an indexer without querying the upstream ICVDB backend for every search.

## Current architecture

```text
                   Torznab request
                         │
                         ▼
                  ┌─────────────┐
                  │   FastAPI   │
                  │    /api     │
                  └──────┬──────┘
                         │
                  normalize request
                         │
                         ▼
                  ┌─────────────┐
                  │ PostgreSQL  │
                  │ local ICVDB │
                  └──────┬──────┘
                         │
                    query results
                         │
                         ▼
                  ┌─────────────┐
                  │   Torznab   │
                  │ XML mapping │
                  └──────┬──────┘
                         │
                         ▼
                  Torznab response
                         │
                         ▼
                      Prowlarr
```

The application and PostgreSQL database are deployed together through Docker Compose.

## Docker architecture

The Compose stack contains two services:

```text
┌────────────────────────────┐
│ Docker Compose             │
│                            │
│  ┌──────────────────────┐  │
│  │ db                   │  │
│  │ PostgreSQL 16        │  │
│  │                      │  │
│  │ volume: icvdb_data   │  │
│  └──────────┬───────────┘  │
│             │              │
│             │ PostgreSQL   │
│             ▼              │
│  ┌──────────────────────┐  │
│  │ icv-torznab          │  │
│  │ FastAPI / Uvicorn    │  │
│  │                      │  │
│  │ port 8000            │  │
│  └──────────────────────┘  │
│                            │
└────────────────────────────┘
```

PostgreSQL is not exposed to the host by default.

The Torznab service connects to PostgreSQL using the internal Docker hostname:

```text
db:5432
```

## Persistent storage

PostgreSQL data is stored in the named Docker volume:

```text
icvdb_data
```

This means restarting or recreating the containers does not normally require restoring the database again.

Removing the volume destroys the local database.

Commands such as:

```bash
docker compose down -v
```

should therefore be used only when database deletion is intentional.

## Database snapshot

The ICVDB dataset is not committed to the Git repository.

Database snapshots are distributed separately through GitHub Releases.

Current snapshot:

```text
Tag: db-2026-08-21
File: icvdb-2026-08-21.dump
Format: PostgreSQL custom dump (pg_dump -Fc)
```

The dump is restored into the local PostgreSQL service with `pg_restore`.

Current installation flow:

```text
Git repository
      │
      ├── application source
      └── Docker Compose
               │
               ▼
        PostgreSQL container
               ▲
               │
        pg_restore
               │
GitHub Release ─┘
   database dump
```

## API

The main endpoint is:

```text
GET /api
```

The Torznab operation is selected using the `t` query parameter.

Examples:

```text
/api?t=caps
/api?t=search&q=example
/api?t=movie&q=example
/api?t=tvsearch&q=example
```

## Supported search modes

### Generic search

```text
t=search
```

Supports:

```text
q
```

### Movie search

```text
t=movie
```

Supports parameters including:

```text
q
imdbid
tmdbid
```

### TV search

```text
t=tvsearch
```

Supports parameters including:

```text
q
season
ep
imdbid
```

## Categories

Current Torznab categories:

| ID | Category |
|---:|---|
| 2000 | Movies |
| 5000 | TV |
| 5070 | TV / Anime |

## Database configuration

The Compose deployment uses:

```text
DB_NAME
DB_USER
DB_PASSWORD
```

The FastAPI service receives:

```text
DB_HOST=db
DB_PORT=5432
DB_NAME
DB_USER
DB_PASSWORD
```

The application also supports overriding all of these values through environment variables.

## Database ownership

ICVDB remains the source of the database schema and release data.

`icvdb-torznab` should treat this schema as external.

The Torznab service should generally perform read-only queries.

The project should not:

- maintain the upstream ICVDB database;
- change the upstream schema;
- introduce application-specific schema migrations without an explicit requirement.

## Identifier normalization

External identifiers may arrive in different formats.

For example, IMDb IDs should be normalized before database comparison.

Normalization logic should remain centralized rather than being duplicated across search modes.

## Torznab XML

Search results are converted from ICVDB records into Torznab/Newznab-compatible XML expected by clients such as Prowlarr.

Compatibility is more important than cosmetic XML changes.

The capabilities endpoint:

```text
/api?t=caps
```

must always reflect features actually implemented by the service.

A successful `caps` request does not prove that PostgreSQL connectivity works because the capabilities response does not require a database query.

A real search should therefore also be used when testing deployments.

## Request flow

A typical request follows this path:

```text
Prowlarr
   │
   │ GET /api?t=movie&...
   ▼
FastAPI
   │
   ├── parse query parameters
   ├── normalize identifiers
   └── determine search mode
   │
   ▼
PostgreSQL
   │
   └── parameterized query
   │
   ▼
ICVDB rows
   │
   ├── normalize result data
   └── map metadata to Torznab
   │
   ▼
Torznab XML
   │
   ▼
Prowlarr
```

## Current self-hosting model

The current version is fully self-hostable, but database initialization is manual.

The user currently performs:

```text
1. clone repository
2. create .env
3. download database snapshot
4. start PostgreSQL
5. restore snapshot with pg_restore
6. start icvdb-torznab
7. configure Prowlarr
```

This design prevents normal indexer searches from placing load on the upstream ICVDB infrastructure.

## Intended snapshot update architecture

A future goal is to automate discovery and installation of new ICVDB snapshots.

The preferred architecture is:

```text
                 ICVDB PostgreSQL
                        │
                        │ periodic pg_dump
                        ▼
                ┌─────────────────┐
                │ Static storage  │
                │                 │
                │ latest.json     │
                │ dump files      │
                └────────┬────────┘
                         │
                    HTTP download
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       self-hosted #1        self-hosted #2
              │                     │
              ▼                     ▼
        local PostgreSQL      local PostgreSQL
              │                     │
              ▼                     ▼
       icvdb-torznab         icvdb-torznab
```

The upstream database would generate one snapshot per release cycle.

The snapshot itself would then be distributed as a static file, avoiding repeated load on the live backend.

## Snapshot manifest

A stable manifest URL could expose the newest available snapshot:

```json
{
  "version": "2026-10-08",
  "url": "https://example.org/icvdb/icvdb-2026-10-08.dump",
  "sha256": "..."
}
```

Example update flow:

```text
Local version: 2026-10-01
Remote version: 2026-10-01
→ nothing to do

Later:

Local version: 2026-10-01
Remote version: 2026-10-08
→ download new dump
→ verify SHA256
→ restore database
→ record version 2026-10-08
```

## Future database update concerns

Automatic snapshot replacement must account for:

- integrity verification;
- failed downloads;
- failed restores;
- avoiding partial databases;
- avoiding unnecessary downtime;
- rollback;
- disk space;
- atomic switching between old and new data where possible.

A future implementation should preferably restore a new snapshot separately and switch over only after successful validation rather than destroying the working database first.

## Snapshot status

Manual snapshot download and restoration are already supported and documented.

Automatic snapshot discovery and updating are not implemented yet.

## Security boundaries

The Torznab API is the only service exposed by the default Compose configuration.

PostgreSQL remains internal to the Docker network.

Database credentials are provided through environment variables.

The application should never expose:

- database passwords;
- internal connection strings;
- sensitive stack traces;
- secrets.

SQL originating from HTTP parameters must always use psycopg parameter binding.

## Design goal

The service should remain a thin compatibility layer.

Responsibilities should remain clearly separated:

```text
ICVDB
    → source data

snapshot publishing
    → distributes source data efficiently

PostgreSQL
    → stores the local snapshot

icvdb-torznab
    → translates database records to Torznab

Prowlarr
    → consumes the Torznab indexer
```

Avoid moving responsibilities between these layers without a concrete reason.
