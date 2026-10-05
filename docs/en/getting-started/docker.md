# Update Violarr

Pull the latest image and recreate the container while retaining the volume.

```bash
docker pull ghcr.io/xbit18/violarr:latest
docker stop icvdb-torznab
docker rm icvdb-torznab
docker run -d \
  --name icvdb-torznab \
  -p 8000:8000 \
  -v icvdb_torznab_data:/data \
  --restart unless-stopped \
  ghcr.io/xbit18/violarr:latest
```

::: danger Do not remove the volume

Do not add `-v` to `docker rm` and do not delete `icvdb_torznab_data` unless you
intend to erase PostgreSQL data, snapshot state, and WebUI settings.

:::

When complete, open the WebUI and confirm that the **Dashboard** shows the
service as **Healthy**.
