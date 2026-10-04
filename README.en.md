# Violarr

[Italiano](README.md) · [English](README.en.md)

**The Prowlarr integration for Il Corsaro Viola.** Violarr is a self-hosted bridge
from an ICVDB PostgreSQL snapshot to Torznab clients such as Prowlarr. One
container runs PostgreSQL 16, FastAPI, the WebUI, and safe automatic database
updates.

> **v1.1.0 status:** the WebUI and configuration work documented below is
> currently unreleased. The implementation is in the project, but the release
> image has not been published and Docker runtime verification is still pending.

## Features

- Torznab searches for movies, TV, and anime
- Persistent browser-based configuration
- Italian-preferred ranking, Italian-only filtering, and bounded custom rules
- Schema-derived Generic Torznab setup in Prowlarr
- SHA256-verified candidate-database snapshot updates with rollback
- One `/data` volume; PostgreSQL is not exposed to the host

## Quick start

```bash
docker run -d \
  --name icvdb-torznab \
  -p 8000:8000 \
  -v icvdb_torznab_data:/data \
  --restart unless-stopped \
  ghcr.io/xbit18/violarr:latest
```

Follow first-start progress:

```bash
docker logs -f icvdb-torznab
```

After a v1.1-capable image starts, open the WebUI at
`http://localhost:8000/`. The Torznab endpoint remains
`http://localhost:8000/api`.

The first start initializes PostgreSQL, downloads the latest snapshot from
[`xbit18/icvdb-snapshots`](https://github.com/xbit18/icvdb-snapshots), verifies
its SHA256 digest, validates and restores it, and then starts FastAPI.

For Compose and upgrade instructions, read the
[public documentation](https://xbit18.github.io/violarr/en/).

## Result processing

The default `unfiltered` preset preserves v1.0 ordering. Optional presets can
prefer explicit Italian markers, hide non-Italian results, or apply structured
score/exclusion rules.

Ranking only changes the ICVDB response; it does not guarantee Radarr or Sonarr
selection. Hard filters remove results before Prowlarr sees them.

## Connect Prowlarr

1. Open **Prowlarr** in the WebUI.
2. Enter the Prowlarr URL and API key.
3. Set the Indexer URL to an address Prowlarr can reach, such as
   `http://icvdb-torznab:8000/api` on a shared Docker network.
4. Save, test the connection, and add the indexer.

Do not use `localhost` for the Indexer URL when Prowlarr runs in another
container: there it refers to the Prowlarr container itself.

## Security

The WebUI, WebAPI, and Torznab endpoint have no authentication. Keep port `8000`
on a trusted LAN or place an authenticated reverse proxy in front of it. The
container does not require a Docker socket, and PostgreSQL listens only on
`127.0.0.1:5432` inside the container.

## Documentation

- [User documentation](https://xbit18.github.io/violarr/en/)
- [Architecture](ARCHITECTURE.md)
- [Changelog](CHANGELOG.md)

## License

MIT
