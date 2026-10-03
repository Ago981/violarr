# ICVDB Torznab

Indexer compatibile con Torznab per ICVDB, pensato per l'utilizzo self-hosted con Prowlarr.

L'applicazione viene eseguita come un singolo container Docker che include:

- PostgreSQL 16
- API Torznab basata su FastAPI
- bootstrap automatico dello snapshot ICVDB
- aggiornamento automatico del database

Gli snapshot del database vengono scaricati da:

https://github.com/xbit18/icvdb-snapshots

## Avvio rapido

### Docker

```bash
docker run -d \
  --name icvdb-torznab \
  -p 8000:8000 \
  -v icvdb_torznab_data:/data \
  --restart unless-stopped \
  ghcr.io/xbit18/icvdb-torznab:latest
```

Al primo avvio il container esegue automaticamente:

1. inizializzazione di PostgreSQL;
2. recupero della release più recente degli snapshot ICVDB;
3. download del dump PostgreSQL;
4. verifica del digest SHA256;
5. validazione del dump;
6. ripristino del database;
7. avvio dell'API Torznab.

Non è necessario configurare o ripristinare manualmente il database.

### Docker Compose

```yaml
services:
  icvdb-torznab:
    image: ghcr.io/xbit18/icvdb-torznab:latest
    container_name: icvdb-torznab
    restart: unless-stopped

    ports:
      - "8000:8000"

    volumes:
      - icvdb_data:/data

    environment:
      DB_AUTO_UPDATE: "true"
      DB_UPDATE_INTERVAL: "86400"

volumes:
  icvdb_data:
    name: icvdb_torznab_data
```

Avvio:

```bash
docker compose up -d
```

Per aggiornare l'immagine dell'applicazione:

```bash
docker compose pull
docker compose up -d
```

## Dati persistenti

Tutti i dati persistenti vengono salvati sotto `/data`.

```text
/data/
├── postgres/
└── state/
    └── snapshot-version
```

Il volume Docker deve quindi essere montato su:

```text
/data
```

La rimozione e ricreazione del container non elimina il database, purché il volume venga mantenuto.

## Aggiornamento automatico del database

Gli snapshot ICVDB vengono pubblicati come GitHub Releases nella repository:

```text
xbit18/icvdb-snapshots
```

L'applicazione controlla:

```text
https://api.github.com/repos/xbit18/icvdb-snapshots/releases/latest
```

La versione dello snapshot installato viene salvata in:

```text
/data/state/snapshot-version
```

Per impostazione predefinita, l'applicazione controlla la disponibilità di un nuovo snapshot ogni 24 ore.

```text
DB_AUTO_UPDATE=true
DB_UPDATE_INTERVAL=86400
```

Quando è disponibile uno snapshot più recente, l'updater esegue:

```text
download snapshot
      ↓
verifica SHA256
      ↓
validazione dump PostgreSQL
      ↓
restore su database candidato
      ↓
validazione database candidato
      ↓
switch dei database
      ↓
salvataggio versione installata
```

Il database corrente continua a essere disponibile durante il download e il restore del nuovo snapshot.

L'API entra in modalità manutenzione solo durante lo switch finale del database. Le richieste ricevute in quel breve intervallo restituiscono HTTP `503`.

Se il download, la validazione o il restore falliscono, il database attualmente funzionante non viene modificato.

## Configurazione

Il container fornisce valori predefiniti e normalmente non richiede variabili d'ambiente aggiuntive.

Opzioni disponibili:

| Variabile | Default | Descrizione |
| --- | --- | --- |
| `DB_AUTO_UPDATE` | `true` | Abilita gli aggiornamenti automatici degli snapshot |
| `DB_UPDATE_INTERVAL` | `86400` | Secondi tra un controllo aggiornamenti e il successivo |
| `DB_UPDATE_START_DELAY` | `60` | Ritardo iniziale prima del primo controllo periodico |
| `SNAPSHOT_LATEST_URL` | GitHub latest release API | Permette di usare una sorgente snapshot alternativa |
| `SNAPSHOT_STATE_FILE` | `/data/state/snapshot-version` | File contenente la versione dello snapshot installato |

La configurazione PostgreSQL è interna al container e non deve essere esposta all'host.

## Endpoint Torznab

L'API è disponibile su:

```text
http://HOST:8000/api
```

Le capabilities possono essere testate con:

```bash
curl 'http://localhost:8000/api?t=caps'
```

Una ricerca generica può essere testata con:

```bash
curl 'http://localhost:8000/api?t=search&limit=10'
```

## Prowlarr

Aggiungi l'indexer come sorgente Torznab generica utilizzando:

```text
http://HOST:8000/api
```

Il parametro API key viene attualmente accettato per compatibilità Torznab, ma non viene utilizzato per l'autenticazione.

## Ricerche supportate

L'indexer supporta attualmente:

- ricerca generica
- ricerca film
- ricerca serie TV
- ricerca tramite IMDb ID
- ricerca tramite TMDb ID

Categorie Torznab:

```text
2000  Movies
5000  TV
5070  TV/Anime
```

## Sviluppo

Build locale dell'immagine:

```bash
docker build -t icvdb-torznab:local .
```

Avvio dell'immagine locale:

```bash
docker run -d \
  --name icvdb-torznab \
  -p 8000:8000 \
  -v icvdb_torznab_data:/data \
  icvdb-torznab:local
```

Log:

```bash
docker logs -f icvdb-torznab
```

## Struttura del progetto

```text
.
├── app.py
├── snapshot_updater.py
├── entrypoint.sh
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── ARCHITECTURE.md
└── README.md
```

## Licenza

MIT
