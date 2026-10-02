# Architecture

## Purpose

`icvdb-torznab` exposes release information stored in an ICVDB PostgreSQL database through a Torznab-compatible API.

Its primary purpose is to allow applications such as Prowlarr to use ICVDB as an indexer.

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
                  │    ICVDB    │
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

## PostgreSQL

Database connectivity is configured using:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

The application currently assumes that the database already exists and has been populated with ICVDB data.

The database should be treated as read-only by this service.

## Identifier normalization

External identifiers may arrive in different formats.

For example, IMDb IDs should be normalized before database comparison.

Normalization logic should remain centralized rather than being duplicated across individual search modes.

## Torznab XML

Search results are converted from ICVDB records into Torznab/Newznab-compatible XML expected by clients such as Prowlarr.

Compatibility is more important than cosmetic XML changes.

The capabilities endpoint:

```text
/api?t=caps
```

must always reflect features actually implemented by the service.

## Intended self-hosted model

The long-term goal is for a user to be able to clone the project and operate a local ICVDB-backed Torznab indexer without placing load on the live ICVDB backend.

The preferred database distribution model is based on periodic snapshots rather than having every installation synchronize directly against the upstream service.

Intended architecture:

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

This avoids repeatedly querying or scraping the upstream ICVDB backend.

The upstream database only needs to generate one snapshot per release cycle; distribution can then be handled by static file hosting.

## Snapshot status

Automatic snapshot retrieval and database restoration are planned but are not currently implemented.

Current deployments still require an existing PostgreSQL database containing ICVDB data.

## Design goal

The service should remain a thin compatibility layer.

Responsibilities should remain clearly separated:

```text
ICVDB
    → source data

database snapshot distribution
    → distributes source data efficiently

PostgreSQL
    → local data storage

icvdb-torznab
    → translates database records to Torznab

Prowlarr
    → consumes the Torznab indexer
```

Avoid moving responsibilities between these layers without a concrete reason.
