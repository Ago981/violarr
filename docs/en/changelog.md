# Changelog

## v1.1.0 — 2026-10-05

v1.1.0 adds:

- persistent schema-v1 WebUI settings with masked Prowlarr secrets;
- deterministic result-processing presets and custom rules;
- same-origin `/webapi` endpoints and schema-derived Prowlarr installation;
- a Vue WebUI served from the single runtime container;
- this bilingual Markdown-first documentation site.

See the repository
[`CHANGELOG.md`](https://github.com/xbit18/violarr/blob/main/CHANGELOG.md) for
compatibility details and the complete project history.

## v1.0 behavior retained

The `/api` Torznab contract, PostgreSQL 16 runtime, port `8000`, one `/data`
volume, snapshot source, and candidate-database update safety remain the
compatibility baseline.
