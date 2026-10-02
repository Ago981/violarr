# ICVDB Torznab

A lightweight Torznab-compatible API for ICVDB, designed to make the database usable as an indexer in applications such as Prowlarr.

The service reads release information from a local PostgreSQL copy of the ICVDB database and exposes it through a Torznab-compatible API.

## Features

- Torznab-compatible API
- Generic search
- Movie search
- TV search
- IMDb ID support
- TMDb ID support
- Season and episode filtering
- Movie, TV and Anime categories
- Docker / Docker Compose deployment
- Bundled PostgreSQL service
- Public ICVDB database snapshot available from GitHub Releases

## Torznab capabilities

The API currently exposes:

- `search`
- `movie-search`
- `tv-search`

Categories:

- `2000` — Movies
- `5000` — TV
- `5070` — TV / Anime

## Requirements

- Docker
- Docker Compose
- `curl` or another way to download the database snapshot

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/xbit18/icvdb-torznab.git
cd icvdb-torznab
```

### 2. Configure the environment

Copy the example file:

```bash
cp .env.example .env
```

Default configuration:

```env
DB_NAME=icv_db
DB_USER=icv
DB_PASSWORD=change-me
```

Change `DB_PASSWORD` before exposing the stack outside a trusted local environment.

### 3. Download the ICVDB snapshot

The current public snapshot is dated **2026-08-21** and is distributed as a PostgreSQL custom-format dump.

```bash
mkdir -p db

curl -L \
  -o db/icvdb-2026-08-21.dump \
  https://github.com/xbit18/icvdb-torznab/releases/download/db-2026-08-21/icvdb-2026-08-21.dump
```

Published SHA256:

```text
446c49abcf8834fabdc9a4013130789cc94173cff86f5c5f50e8812b184a99b8
```

Optional verification:

```bash
echo "446c49abcf8834fabdc9a4013130789cc94173cff86f5c5f50e8812b184a99b8  db/icvdb-2026-08-21.dump" | sha256sum -c -
```

You can also download the snapshot manually from the [GitHub Releases](https://github.com/xbit18/icvdb-torznab/releases) page.

### 4. Start PostgreSQL

```bash
docker compose up -d db
```

Wait until the database is healthy:

```bash
docker compose ps
```

### 5. Restore the snapshot

On the first installation, restore the downloaded dump into the local PostgreSQL container:

```bash
docker compose exec -T db \
  sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-privileges' \
  < db/icvdb-2026-08-21.dump
```

The PostgreSQL data is stored in the Docker volume `icvdb_data`, so the restore only needs to be performed when initializing the database or when deliberately replacing it with a newer snapshot.

### 6. Start the Torznab service

```bash
docker compose up -d --build
```

The API will be available at:

```text
http://localhost:8000/api
```

## Verify the installation

Check Torznab capabilities:

```bash
curl 'http://localhost:8000/api?t=caps'
```

A real search can be used to verify that the API is also reaching PostgreSQL:

```bash
curl -s 'http://localhost:8000/api?t=search&q=avatar'
```

The response should be Torznab-compatible XML.

## Prowlarr

Add the service to Prowlarr as a **Generic Torznab** indexer.

Use:

```text
http://<server-ip>:8000/api
```

as the Torznab URL.

No API key is currently required by this service.

If Prowlarr runs in another Docker container, use an address that is reachable from that container rather than `localhost`.

## API examples

Capabilities:

```text
/api?t=caps
```

Generic search:

```text
/api?t=search&q=example
```

Movie search:

```text
/api?t=movie&q=example
```

TV search:

```text
/api?t=tvsearch&q=example
```

## Database snapshots

Database snapshots are intentionally distributed through GitHub Releases rather than committed to the Git repository because they are large binary files.

The current snapshot:

- Date: **2026-08-21**
- Format: PostgreSQL custom dump (`pg_dump -Fc`)
- File: `icvdb-2026-08-21.dump`
- Size: approximately 340 MB
- SHA256: `446c49abcf8834fabdc9a4013130789cc94173cff86f5c5f50e8812b184a99b8`

Automatic database snapshot discovery and updating are not implemented yet. Updating to a future snapshot currently requires downloading and restoring it manually.

## Docker services

The Compose stack contains:

- `db` — PostgreSQL 16 containing the local ICVDB snapshot
- `icv-torznab` — FastAPI service exposing the Torznab API

Database contents persist in the `icvdb_data` Docker volume.

## Security

Database credentials should be stored in `.env`.

The `.env` file and local database dumps are ignored by Git and must not be committed.

The default deployment exposes only the Torznab API on port `8000`; PostgreSQL is not published to the host.

## Disclaimer

This project provides a Torznab-compatible interface for a local copy of the ICVDB database.

It does not host, distribute, or download media or torrent payloads.

## License

MIT
