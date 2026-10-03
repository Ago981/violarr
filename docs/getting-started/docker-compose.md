# Docker Compose

## Compose file

```yaml
services:
  icvdb-torznab:
    image: ghcr.io/xbit18/icvdb-torznab:latest
    container_name: icvdb-torznab
    restart: unless-stopped
    ports:
      - '8000:8000'
    volumes:
      - icvdb_data:/data
    environment:
      DB_AUTO_UPDATE: 'true'
      DB_UPDATE_INTERVAL: '86400'

volumes:
  icvdb_data:
    name: icvdb_torznab_data
```

Start it:

```bash
docker compose up -d
docker compose logs -f icvdb-torznab
```

Update the image without removing data:

```bash
docker compose pull
docker compose up -d
```

::: warning Volume safety Do not run `docker compose down -v` unless permanent
data deletion is intended. :::

For configuration choices, see
[environment variables](../configuration/environment).
