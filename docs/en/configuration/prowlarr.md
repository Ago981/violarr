# Prowlarr integration

Configure Prowlarr from the WebUI instead of manually creating a Generic Torznab
indexer.

## Quick path

1. Open **Prowlarr** in the WebUI.
2. Enter the Prowlarr URL, for example `http://prowlarr:9696`.
3. Enter a Prowlarr API key.
4. Enter the Indexer URL that **Prowlarr can reach**, for example
   `http://icvdb-torznab:8000/api`.
5. Save, choose **Test connection**, then choose **Add indexer**.

<div class="prowlarr-note">
<strong>Container networking:</strong> <code>localhost</code> inside the Prowlarr
container refers to Prowlarr itself. Use a shared Docker network service name or
another address reachable from that container.
</div>

## What Test and Add do

**Test connection** requests Prowlarr's `/api/v1/indexer/schema` endpoint with
the `X-Api-Key` header.

**Add indexer** follows Prowlarr's current schema instead of constructing an
unversioned request by hand:

1. Fetch the indexer schemas and select the Generic Torznab template whose
   implementation is `Torznab`.
2. Deep-clone that template and set its display name to `Violarr`.
3. Split the configured Indexer URL into `baseUrl` and `apiPath`, and populate
   those schema fields. Set the Torznab `apiKey` field to an empty string
   because Violarr does not authenticate `/api`.
4. Read existing indexers and compare Torznab implementations by normalized
   origin and API path.
5. If no match exists, ask Prowlarr to test the completed resource and then
   create it.

An existing normalized endpoint is returned without another test or create
request. Repeated Add operations are therefore idempotent.

## API-key handling

- The key is saved only when entered.
- Leaving the replacement field absent preserves the persisted key.
- Sending an empty replacement clears the persisted key.
- Read responses contain `api_key_configured`, never the key.
- Runtime API-key overrides are never copied into the settings file.

## Failure responses

`GET /webapi/prowlarr/status` always returns HTTP `200`. Connection and remote
response failures appear as `connected: false` with an `error` string in the
status payload. Normally that string keeps a sanitized specific reason such as
an HTTP status, connection failure, oversized response, invalid JSON, or invalid
schema.

If a status error contains the configured API key or the word `traceback`, the
WebAPI replaces it with `Prowlarr request failed`. Unexpected client setup
errors are also reduced to that message. The `POST` test and indexer routes use
HTTP `502` with the same stable detail for remote Prowlarr failures; missing
required configuration returns HTTP `400`.
