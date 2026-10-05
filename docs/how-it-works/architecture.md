# Architettura

Violarr usa un solo container e un solo volume persistente.

```text
Client / Prowlarr
       │ :8000
       ▼
FastAPI ── /          Vue WebUI
        ├─ /webapi    settings and Prowlarr operations
        └─ /api       Torznab XML
       │
       ▼
PostgreSQL 16 on 127.0.0.1:5432
       │
       ▼
/data/postgres + /data/state
```

L'immagine Docker compila Vue in uno stage Node e copia nel runtime
PostgreSQL/Python solo gli asset di produzione. FastAPI monta gli asset dopo
aver registrato `/api` e `/webapi`, quindi il fallback SPA non può nascondere le
route API.

## Flussi delle richieste

### Torznab

```text
query parameters → parameterized SQL → 1000-row processing window when enabled
                 → Torznab item mapping → XML response
```

### WebUI

```text
browser → static Vue assets → same-origin /webapi → settings/updater/Prowlarr
```

### Aggiornamento snapshot

```text
GitHub release → SHA256 + dump validation → candidate database validation
               → maintenance switch → post-switch validation → state update
```

Per moduli e invarianti destinati ai maintainer consulta
[`ARCHITECTURE.md`](https://github.com/xbit18/violarr/blob/main/ARCHITECTURE.md).
