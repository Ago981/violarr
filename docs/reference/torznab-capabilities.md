# Funzionalità Torznab

Richiedi le funzionalità con:

```bash
curl 'http://localhost:8000/api?t=caps'
```

## Ricerche dichiarate

| Operazione | Parametri dichiarati          |
| ---------- | ----------------------------- |
| `search`   | `q`                           |
| `movie`    | `q`, `imdbid`, `tmdbid`       |
| `tvsearch` | `q`, `season`, `ep`, `imdbid` |

Tutte le richieste accettano anche `t`, `cat`, `limit`, `offset`, `apikey` ed
`extended`. `cat`, `apikey` ed `extended` sono accettati per compatibilità ma
non modificano la ricerca.

`limit` vale 100 per default e deve essere 1–200. `offset` vale 0 e non può
essere negativo. Gli IMDb ID numerici sono normalizzati aggiungendo `tt`.

## Categorie

| ID     | Nome     | Mappatura                          |
| ------ | -------- | ---------------------------------- |
| `2000` | Movies   | Tipo database `movie`              |
| `5000` | TV       | Altri tipi diversi da film e anime |
| `5070` | TV/Anime | Tipo database `anime`              |

## Risposta XML

Le ricerche restituiscono XML RSS 2.0. Ogni risultato può contenere titolo, GUID
info-hash non permalink, magnet link, `pubDate` UTC facoltativa, enclosure
BitTorrent e attributi Torznab `category`, `infohash`, `magneturl`, `seeders`,
`peers`, `size` facoltativo, `downloadvolumefactor=0`, `uploadvolumefactor=1` e
`description` facoltativa del provider.

Valori `t` sconosciuti producono un feed RSS vuoto valido. La serializzazione
XML esegue l'escaping dei valori. Con l'elaborazione attiva, la paginazione usa
[finestre fisse di 1000 righe](../how-it-works/result-processing).
