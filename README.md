# Violarr

<img src="docs/public/logo.png" alt="Logo di Violarr" width="180">

[![GitHub Release](https://img.shields.io/github/v/release/xbit18/violarr?color=blue)](https://github.com/xbit18/violarr/releases)
[![GitHub License](https://img.shields.io/github/license/xbit18/violarr?color=green)](/LICENSE)

[Italiano](README.md) · [English](README.en.md)

**Violarr ti permette di usare direttamente con Prowlarr il ricco database
ICVDB.**

## Funzionalità

- Cerca film, serie TV e anime da Prowlarr.
- Configura tutto dalla WebUI in italiano o inglese.
- Preferisci i risultati italiani o crea regole personalizzate.
- Mantieni il database aggiornato automaticamente.

## Avvio rapido

```bash
docker run -d \
  --name icvdb-torznab \
  -p 8000:8000 \
  -v icvdb_torznab_data:/data \
  --restart unless-stopped \
  ghcr.io/xbit18/violarr:latest
```

Quando il servizio è pronto, apri `http://localhost:8000/` e completa la
[prima configurazione](https://xbit18.github.io/violarr/getting-started/first-setup).

## Documentazione

- [Installazione, configurazione e utilizzo](https://xbit18.github.io/violarr/)
- [Architecture](ARCHITECTURE.md)
- [Changelog](CHANGELOG.md)

## Licenza

MIT
