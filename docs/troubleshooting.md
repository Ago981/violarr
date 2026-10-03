# Troubleshooting

Start with container logs:

```bash
docker logs -f icvdb-torznab
```

## WebUI does not open

- Confirm port `8000` is published.
- Check `curl 'http://localhost:8000/api?t=caps'`.
- The public `latest` image may still be v1.0 until v1.1.0 is published; v1.0
  has no WebUI.
- A source checkout must build frontend assets before FastAPI can serve them.

## First start takes a long time

Fresh installations download, verify, inspect, and restore a PostgreSQL dump
before FastAPI starts. Follow the logs and preserve the `/data` volume between
retries.

## Prowlarr Test fails

1. Confirm the Prowlarr URL is reachable from the ICVDB container.
2. Confirm the API key in Prowlarr under **Settings → General**.
3. If both applications are containers, do not use `localhost` unless they share
   the same network namespace.
4. Confirm Prowlarr exposes the Generic Torznab schema.

## Add succeeds but searches fail

The Indexer URL must be reachable from the **Prowlarr container** and end at
`/api`. Test it from the relevant network, not only from the host browser.

## Expected releases are missing

- `italian_only` and custom exclusion rules are hard filters.
- Ranking is local to 1000-row database windows.
- Result processing cannot guarantee Radarr/Sonarr selection.
- Switch back to `unfiltered` to compare the original database order.

## Update is temporarily unavailable

HTTP `503` with `Retry-After: 5` is expected during the short database switch.
Persistent updater errors appear on the WebUI dashboard and in logs. The active
database remains unchanged for failures before the switch.

## Settings do not match the saved file

Check [environment variables](./configuration/environment). Runtime overrides
win over persisted values without rewriting `settings.json`.
