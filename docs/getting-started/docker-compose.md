# Docker Compose

Avvia e aggiorna Violarr con un file Compose mantenendo i dati tra le
ricreazioni.

## File Compose

```yaml
services:
  icvdb-torznab:
    image: ghcr.io/xbit18/violarr:latest
    container_name: icvdb-torznab
    restart: unless-stopped
    ports:
      - '8000:8000'
    volumes:
      - icvdb_data:/data
volumes:
  icvdb_data:
    name: icvdb_torznab_data
```

Avvia il servizio:

```bash
docker compose up -d
docker compose logs -f icvdb-torznab
```

Aggiorna l'immagine senza rimuovere i dati:

```bash
docker compose pull
docker compose up -d
```

::: warning Sicurezza del volume

Non eseguire `docker compose down -v` a meno che l'eliminazione permanente dei
dati sia intenzionale.

:::

Per le opzioni disponibili consulta le
[variabili d'ambiente](../configuration/environment).
