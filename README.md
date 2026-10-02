# ICVDB Torznab

A lightweight Torznab-compatible API for [ICVDB](https://github.com/ICV-Crew/ICVDB), designed to make the database usable as an indexer in applications such as Prowlarr.

The service reads release information from an existing ICVDB PostgreSQL database and exposes it through a Torznab-compatible API.

## Features

- Torznab-compatible API
- Generic search
- Movie search
- TV search
- IMDb ID support
- TMDb ID support
- Season and episode filtering
- Movie, TV and Anime categories
- Docker support
- Configurable PostgreSQL connection

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
- A running PostgreSQL database populated by ICVDB

## Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Then configure the PostgreSQL connection:

```env
DB_HOST=host.docker.internal
DB_PORT=5433
DB_NAME=icv_db
DB_USER=icv
DB_PASSWORD=your-password
```

## Running with Docker Compose

Build and start the service:

```bash
docker compose up -d --build
```

The Torznab API will be available at:

```text
http://localhost:8000/api
```

You can verify the service with:

```bash
curl 'http://localhost:8000/api?t=caps'
```

## Prowlarr

Add the service to Prowlarr as a generic Torznab indexer.

Use:

```text
http://<server-ip>:8000/api
```

as the Torznab URL.

No API key is currently required by this service.

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

## Security

Database credentials should be stored in `.env`.

The `.env` file is ignored by Git and must not be committed.

## Disclaimer

This project only provides a Torznab-compatible interface for an existing ICVDB database.

It does not host, distribute, or download media or torrent files.

## License

MIT
