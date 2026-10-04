# Installation

Run one container with one persistent volume. No external PostgreSQL service or
Docker socket is required.

## Quick path

```bash
docker run -d \
  --name icvdb-torznab \
  -p 8000:8000 \
  -v icvdb_torznab_data:/data \
  --restart unless-stopped \
  ghcr.io/xbit18/violarr:latest
```

The first start initializes PostgreSQL 16, downloads and validates the latest
ICVDB snapshot, restores it, and then starts FastAPI. Bootstrap can take time.

When the service is ready:

- WebUI: `http://localhost:8000/`
- Torznab: `http://localhost:8000/api`
- WebAPI: `http://localhost:8000/webapi`

## Persistent data

Mount exactly one volume at `/data`. It holds the PostgreSQL cluster and state
files. Replacing the container is safe when the volume is retained; deleting the
volume deletes the local database and settings.

## Next step

Continue with [first setup](./first-setup) or use the
[Docker Compose example](./docker-compose).
