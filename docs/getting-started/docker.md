# Docker

## Avvio e controllo

```bash
docker run -d \
  --name icvdb-torznab \
  -p 8000:8000 \
  -v icvdb_torznab_data:/data \
  --restart unless-stopped \
  ghcr.io/xbit18/violarr:latest

docker logs -f icvdb-torznab
```

Viene pubblicata solo la porta FastAPI `8000`. PostgreSQL ascolta su
`127.0.0.1:5432` nel container e non è esposto all'host.

## Aggiornare l'immagine

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

Il volume denominato sopravvive alla sostituzione del container.

::: danger Non rimuovere il volume

Non aggiungere `-v` a `docker rm` e non eliminare `icvdb_torznab_data` a meno
che tu voglia cancellare dati PostgreSQL, stato degli snapshot e impostazioni
WebUI.

:::

## Aggiornamento del volume v1.0

v1.1 mantiene percorso dati PostgreSQL 16, file di stato, porta e contratto del
volume `/data`. Al primo avvio crea `/data/state/settings.json` con i valori
predefiniti e riutilizza il database esistente. La verifica Docker end-to-end
con un volume v1.0 reale è ancora in sospeso.
