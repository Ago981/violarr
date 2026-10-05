# Installation

Start Violarr and reach the WebUI with one command.

You need Docker and an internet connection for the first start.

## Quick path

```bash
docker run -d \
  --name icvdb-torznab \
  -p 8000:8000 \
  -v icvdb_torznab_data:/data \
  --restart unless-stopped \
  ghcr.io/xbit18/violarr:latest
```

The first start can take a few minutes. Follow its progress with
`docker logs -f icvdb-torznab`.

When the service is ready:

- the logs report that the service is ready;
- the WebUI opens at `http://localhost:8000/`;
- the dashboard shows the database as connected.

## Next step

Continue with [first setup](./first-setup).
