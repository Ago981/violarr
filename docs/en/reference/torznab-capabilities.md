# Torznab capabilities

Request capabilities with:

```bash
curl 'http://localhost:8000/api?t=caps'
```

## Advertised searches

| Operation  | Advertised parameters         |
| ---------- | ----------------------------- |
| `search`   | `q`                           |
| `movie`    | `q`, `imdbid`, `tmdbid`       |
| `tvsearch` | `q`, `season`, `ep`, `imdbid` |

All requests also accept `t`, `cat`, `limit`, `offset`, `apikey`, and `extended`
at the HTTP layer. `cat`, `apikey`, and `extended` are accepted for
compatibility but do not currently change search behavior.

`limit` defaults to 100 and must be 1–200. `offset` defaults to 0 and must be
non-negative. Numeric IMDb IDs are normalized by adding the `tt` prefix.

## Categories

| ID     | Name     | Mapping                          |
| ------ | -------- | -------------------------------- |
| `2000` | Movies   | Database type `movie`            |
| `5000` | TV       | Other non-movie, non-anime types |
| `5070` | TV/Anime | Database type `anime`            |

## XML response

Searches return RSS 2.0 XML. Each result can contain:

- title, non-permalink info-hash GUID, magnet link, and optional UTC `pubDate`;
- a BitTorrent enclosure with magnet URL and optional byte length;
- Torznab attributes `category`, `infohash`, `magneturl`, `seeders`, `peers`,
  optional `size`, `downloadvolumefactor=0`, `uploadvolumefactor=1`, and
  optional provider `description`.

Unknown `t` values return a valid empty RSS feed. Database and input values are
escaped by XML element serialization.

When result processing is enabled, pagination uses
[fixed 1000-row windows](../how-it-works/result-processing).
