# Connect Prowlarr

Connect Prowlarr from the WebUI and add Violarr as an indexer.

## Quick path

1. In Prowlarr, copy the key from **Settings → General → Security → API Key**.
2. Open **Prowlarr** in the Violarr WebUI.
3. Enter the **Prowlarr URL**, for example `http://prowlarr:9696`.
4. Enter the **API key**.
5. Enter the **Indexer URL as seen by Prowlarr**, for example
   `http://icvdb-torznab:8000/api`.
6. Select **Save Prowlarr settings**, then **Test connection**.
7. When the status is **Connected**, select **Add Violarr to Prowlarr**.

<div class="prowlarr-note">
<strong>Container networking:</strong> <code>localhost</code> inside the Prowlarr
container refers to Prowlarr itself. Use a shared Docker network service name or
another address reachable from that container.
</div>

## Expected result

- The WebUI shows **Connected**.
- Prowlarr contains an indexer named **Violarr**.
- Adding it again does not create duplicates.

## Change the key

- A saved key remains active until you select **Replace key** or **Clear the
  saved API key**, then save.
- If the test fails, check the URLs, key, and container networking in
  [troubleshooting](../troubleshooting).
