# Architettura

## Panoramica

`icvdb-torznab` è un indexer compatibile con Torznab basato su ICVDB.

Il progetto viene distribuito come un singolo container Docker che contiene:

```text
┌───────────────────────────────────────┐
│ container icvdb-torznab              │
│                                       │
│  PostgreSQL 16                        │
│  FastAPI / Uvicorn                    │
│  Snapshot updater                     │
│                                       │
│  /data                                │
│  ├── postgres/                        │
│  └── state/snapshot-version           │
└───────────────────────────────────────┘
```

All'host viene esposta soltanto l'API HTTP.

PostgreSQL ascolta su `127.0.0.1:5432` all'interno del container e non viene esposto esternamente.

## Componenti

### Applicazione FastAPI

`app.py` implementa l'API compatibile con Torznab.

Si collega a PostgreSQL tramite:

```text
127.0.0.1:5432
```

I parametri di connessione al database sono valori interni forniti dal container.

L'applicazione FastAPI installa inoltre gli hook di lifecycle dello snapshot updater.

### PostgreSQL

Il container è basato su PostgreSQL 16.

I dati persistenti di PostgreSQL vengono salvati in:

```text
/data/postgres
```

Al primo avvio, `entrypoint.sh` inizializza il cluster PostgreSQL e crea il database applicativo.

Agli avvii successivi viene riutilizzato il cluster PostgreSQL già presente nel volume Docker.

### Entrypoint

`entrypoint.sh` gestisce il ciclo di vita del container.

Flusso di avvio:

```text
avvio container
      ↓
inizializzazione PostgreSQL se necessaria
      ↓
avvio PostgreSQL
      ↓
attesa disponibilità PostgreSQL
      ↓
creazione database applicativo se necessario
      ↓
snapshot già installato?
   ┌──┴──┐
   no   sì
   ↓      ↓
bootstrap latest snapshot
   ↓
avvio FastAPI
```

L'entrypoint gestisce anche lo shutdown del container e arresta in modo pulito sia Uvicorn sia PostgreSQL.

`tini` viene utilizzato come PID 1 per il corretto inoltro dei segnali e la gestione dei processi figli.

## Sorgente degli snapshot

Gli snapshot del database vengono distribuiti separatamente tramite:

```text
https://github.com/xbit18/icvdb-snapshots
```

L'updater interroga:

```text
https://api.github.com/repos/xbit18/icvdb-snapshots/releases/latest
```

Ogni release contiene un dump PostgreSQL in formato custom:

```text
icvdb-YYYY-MM-DD.dump
```

GitHub espone il digest SHA256 dell'asset tramite la Releases API.

La versione installata viene salvata in:

```text
/data/state/snapshot-version
```

Esempio:

```text
db-2026-10-04
```

## Bootstrap iniziale

Se il file con la versione dello snapshot non esiste, il container esegue il bootstrap iniziale prima di avviare FastAPI.

L'updater esegue:

```text
recupero metadata latest release
      ↓
download asset .dump
      ↓
verifica SHA256
      ↓
pg_restore --list
      ↓
restore database candidato
      ↓
validazione database candidato
      ↓
switch del database
      ↓
scrittura snapshot-version
```

FastAPI viene avviata solo dopo il completamento con successo del bootstrap iniziale.

Questo evita che l'API venga avviata contro un database vuoto durante una nuova installazione.

## Aggiornamenti automatici

Dopo l'avvio di FastAPI, l'updater viene eseguito periodicamente all'interno del processo applicativo.

Valori predefiniti:

```text
DB_AUTO_UPDATE=true
DB_UPDATE_INTERVAL=86400
DB_UPDATE_START_DELAY=60
```

L'intervallo viene calcolato dal completamento di un controllo aggiornamenti all'inizio di quello successivo.

Di conseguenza, due aggiornamenti non possono sovrapporsi anche se un update impiega più tempo dell'intervallo configurato.

È inoltre presente un lock interno che impedisce l'esecuzione concorrente di più aggiornamenti.

## Sicurezza dell'aggiornamento

Gli aggiornamenti non vengono mai ripristinati direttamente sul database attivo.

L'updater crea invece:

```text
icv_db_candidate
```

e ripristina lì il nuovo snapshot.

Il database attivo rimane:

```text
icv_db
```

e continua a servire le richieste durante download, restore e validazione del database candidato.

### Validazione

Prima dello switch vengono verificati:

1. digest SHA256 fornito da GitHub;
2. validità del dump tramite `pg_restore --list`;
3. completamento di `pg_restore` con `--exit-on-error`;
4. connessione al database candidato;
5. presenza di tabelle utente nel database candidato.

### Switch del database

Dopo la validazione:

```text
icv_db           → icv_db_previous
icv_db_candidate → icv_db
```

Durante questa breve operazione viene attivata la modalità manutenzione.

Le richieste HTTP ricevute durante la manutenzione restituiscono:

```text
503 Service Unavailable
```

Dopo lo switch, il nuovo `icv_db` viene validato nuovamente.

Se la validazione ha successo:

```text
scrittura snapshot-version
eliminazione icv_db_previous
disattivazione maintenance mode
```

Se la validazione fallisce, l'updater tenta di ripristinare `icv_db_previous` come database attivo.

## Gestione degli errori

### Errore di download

Il database attivo non viene modificato.

### SHA256 non valido

Il file scaricato viene eliminato e il database attivo non viene modificato.

### Dump non valido

L'aggiornamento viene interrotto prima del restore.

### Errore nel restore del database candidato

Il database candidato viene eliminato e il database attivo rimane invariato.

### Validazione fallita del database candidato

Il database candidato viene eliminato e il database attivo rimane invariato.

### Validazione fallita dopo lo switch

L'updater tenta di ripristinare `icv_db_previous` come database attivo.

La versione installata viene aggiornata solo dopo uno switch completato con successo.

## Persistenza

Viene utilizzato un singolo volume Docker:

```text
-v icvdb_torznab_data:/data
```

Contenuto:

```text
/data/
├── postgres/
│   └── cluster PostgreSQL
└── state/
    └── snapshot-version
```

La ricreazione del container preserva quindi sia il database sia la versione dello snapshot installato.

## Networking

Esposto verso l'esterno:

```text
8000/tcp → FastAPI
```

Solo interno al container:

```text
5432/tcp → PostgreSQL su 127.0.0.1
```

Non è necessario pubblicare la porta PostgreSQL.

## Docker Compose

La configurazione Compose utilizza la stessa architettura single-container e scarica l'immagine pubblicata su GHCR:

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

Docker Compose è opzionale. La stessa immagine può essere avviata direttamente con `docker run`.

## Distribuzione

L'immagine viene pubblicata su GitHub Container Registry:

```text
ghcr.io/xbit18/icvdb-torznab
```

L'architettura runtime non dipende dal meccanismo di distribuzione: bootstrap e aggiornamento del database funzionano allo stesso modo sia con `docker run` sia con Docker Compose.
