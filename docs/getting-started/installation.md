# Installazione

Esegui un solo container con un solo volume persistente. Non servono un servizio
PostgreSQL esterno né un socket Docker.

## Procedura rapida

```bash
docker run -d \
  --name icvdb-torznab \
  -p 8000:8000 \
  -v icvdb_torznab_data:/data \
  --restart unless-stopped \
  ghcr.io/xbit18/violarr:latest
```

Il primo avvio inizializza PostgreSQL 16, scarica e convalida l'ultimo snapshot
ICVDB, lo ripristina e avvia FastAPI. L'inizializzazione può richiedere tempo.

Quando il servizio è pronto:

- WebUI: `http://localhost:8000/`
- Torznab: `http://localhost:8000/api`
- WebAPI: `http://localhost:8000/webapi`

## Dati persistenti

Monta esattamente un volume su `/data`: contiene il cluster PostgreSQL e i file
di stato. Puoi sostituire il container conservando il volume; eliminare il
volume cancella database e impostazioni locali.

## Passo successivo

Continua con la [prima configurazione](./first-setup) oppure usa l'esempio
[Docker Compose](./docker-compose).
