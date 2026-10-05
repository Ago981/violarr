# Architecture

Violarr remains one container and one persisted volume.

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

The Docker image builds the Vue application in a Node stage, then copies only
its production assets into the PostgreSQL/Python runtime. FastAPI mounts those
assets after registering `/api` and `/webapi`, so SPA fallback cannot shadow API
routes.

## Request flows

### Torznab

```text
query parameters → parameterized SQL → 1000-row processing window when enabled
                 → Torznab item mapping → XML response
```

### WebUI

```text
browser → static Vue assets → same-origin /webapi → settings/updater/Prowlarr
```

### Snapshot update

```text
GitHub release → SHA256 + dump validation → candidate database validation
               → maintenance switch → post-switch validation → state update
```

For maintainer-level module and invariant details, see the repository
[`ARCHITECTURE.md`](https://github.com/xbit18/violarr/blob/main/ARCHITECTURE.md).
