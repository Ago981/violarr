# Docker

## Start and inspect

```bash
docker run -d \
  --name icvdb-torznab \
  -p 8000:8000 \
  -v icvdb_torznab_data:/data \
  --restart unless-stopped \
  ghcr.io/xbit18/violarr:latest

docker logs -f icvdb-torznab
```

Only FastAPI port `8000` is published. PostgreSQL listens on `127.0.0.1:5432`
inside the container and is not exposed to the host.

## Update the application image

```bash
docker pull ghcr.io/xbit18/violarr:latest
docker stop icvdb-torznab
docker rm icvdb-torznab
docker run -d \
  --name icvdb-torznab \
  -p 8000:8000 \
  -v icvdb_torznab_data:/data \
  --restart unless-stopped \
  ghcr.io/xbit18/violarr:latest
```

The named volume survives container replacement.

::: danger Do not remove the volume

Do not add `-v` to `docker rm` and do not delete `icvdb_torznab_data` unless you
intend to erase PostgreSQL data, snapshot state, and WebUI settings.

:::

## v1.0 volume upgrade

v1.1 keeps the same PostgreSQL 16 data path, snapshot state file, image port,
and `/data` volume contract. On first v1.1 startup, the settings store creates
`/data/state/settings.json` with defaults while reusing existing database data.

The upgrade path is designed for backward compatibility, but end-to-end Docker
verification with an actual v1.0 volume is still pending.
