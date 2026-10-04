# Prima configurazione

## Procedura rapida

1. Attendi nei log il completamento del ripristino iniziale.
2. Apri `http://localhost:8000/`.
3. Verifica che la dashboard indichi il database come connesso.
4. Scegli un [preset di elaborazione](../configuration/result-processing).
5. Configura e verifica [Prowlarr](../configuration/prowlarr).

Prova direttamente Torznab:

```bash
curl 'http://localhost:8000/api?t=caps'
curl -s 'http://localhost:8000/api?t=search&q=avatar&limit=10'
```

## Cosa crea il primo avvio

```text
/data/
├── postgres/                PostgreSQL 16 cluster
└── state/
    ├── settings.json        schema v1 WebUI settings
    └── snapshot-version     installed snapshot tag
```

Le impostazioni sono scritte atomicamente. Gli override d'ambiente modificano la
configurazione effettiva, ma non sovrascrivono i valori memorizzati.

## Sicurezza prima della condivisione

WebUI, WebAPI ed endpoint Torznab non hanno autenticazione. Non pubblicare la
porta `8000` direttamente su Internet: usa una LAN affidabile, il firewall
dell'host o un reverse proxy autenticato.
