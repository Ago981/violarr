# First setup

## Quick path

1. Wait for the initial snapshot restore to finish in the container logs.
2. Open `http://localhost:8000/`.
3. Confirm that the dashboard reports the database as connected.
4. Choose a [result-processing preset](../configuration/result-processing).
5. Configure and test [Prowlarr](../configuration/prowlarr).

Test Torznab directly:

```bash
curl 'http://localhost:8000/api?t=caps'
curl -s 'http://localhost:8000/api?t=search&q=avatar&limit=10'
```

## What the first start creates

```text
/data/
├── postgres/                PostgreSQL 16 cluster
└── state/
    ├── settings.json        schema v1 WebUI settings
    └── snapshot-version     installed snapshot tag
```

Settings are written atomically. Runtime environment overrides affect the
effective configuration but do not overwrite stored values.

## Security before sharing

There is no user authentication for the WebUI, WebAPI, or Torznab endpoint. Do
not publish port `8000` directly to the internet. Use a trusted LAN, host
firewall, or authenticated reverse proxy.
