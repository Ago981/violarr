# Violarr

<img src="docs/public/logo.png" alt="Violarr logo" width="180">

[![GitHub Release](https://img.shields.io/github/v/release/xbit18/violarr?color=blue)](https://github.com/xbit18/violarr/releases)
[![GitHub License](https://img.shields.io/github/license/xbit18/violarr?color=green)](/LICENSE)

[Italiano](README.md) · [English](README.en.md)

**Violarr lets you use the rich ICVDB database directly with Prowlarr.**

## Features

- Search movies, TV, and anime from Prowlarr.
- Configure everything from the WebUI in Italian or English.
- Prefer Italian results or build custom rules.
- Keep the database updated automatically.

## Quick start

```bash
docker run -d \
  --name icvdb-torznab \
  -p 8000:8000 \
  -v icvdb_torznab_data:/data \
  --restart unless-stopped \
  ghcr.io/xbit18/violarr:latest
```

When the service is ready, open `http://localhost:8000/` and complete the
[first setup](https://xbit18.github.io/violarr/en/getting-started/first-setup).

## Documentation

- [Installation, setup, and usage](https://xbit18.github.io/violarr/en/)
- [Architecture](ARCHITECTURE.md)
- [Changelog](CHANGELOG.md)

## License

MIT
