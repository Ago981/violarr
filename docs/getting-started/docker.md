# Aggiornare Violarr

Scarica l'immagine più recente e ricrea il container conservando il volume.

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

::: danger Non rimuovere il volume

Non aggiungere `-v` a `docker rm` e non eliminare `icvdb_torznab_data` a meno
che tu voglia cancellare dati PostgreSQL, stato degli snapshot e impostazioni
WebUI.

:::

Al termine, apri la WebUI e verifica che **Panoramica** mostri il servizio come
**Operativo**.
