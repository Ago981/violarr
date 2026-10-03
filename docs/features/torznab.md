# Torznab

ICVDB Torznab exposes one endpoint at `/api` for Prowlarr and other compatible
clients.

Supported operations:

- `t=caps`
- `t=search`
- `t=movie`
- `t=tvsearch`

The endpoint returns XML generated with Python's XML element API, so titles and
database values are escaped rather than concatenated into markup.

Start with the [capabilities reference](../reference/torznab-capabilities) for
parameters, categories, limits, and emitted attributes.
