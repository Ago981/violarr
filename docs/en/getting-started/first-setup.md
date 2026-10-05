# First setup

Complete the initial setup from the WebUI.

1. Open `http://localhost:8000/`.
2. Under **Dashboard**, confirm that the service is **Healthy**.
3. Keep **Unfiltered** to start, or choose a
   [result-processing preset](../configuration/result-processing).
4. [Connect Prowlarr](../configuration/prowlarr).

If the service is not healthy, select **Refresh**. If the status stays red, open
[troubleshooting](../troubleshooting).

## Security before sharing

The WebUI has no authentication. Do not publish port `8000` directly to the
internet. Use a trusted LAN or an authenticated reverse proxy.
