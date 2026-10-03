import os
from snapshot_updater import install_snapshot_updater
from fastapi import FastAPI, Query, Response
import psycopg
from result_processor import process_results
from settings import SettingsStore
from xml.etree.ElementTree import (
    Element,
    SubElement,
    tostring,
    register_namespace,
)

app = FastAPI()
install_snapshot_updater(app)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "host.docker.internal"),
    "port": int(os.getenv("DB_PORT", "5433")),
    "dbname": os.getenv("DB_NAME", "icv_db"),
    "user": os.getenv("DB_USER", "icv"),
    "password": os.getenv("DB_PASSWORD", ""),
}

TORZNAB_NS = "http://torznab.com/schemas/2015/feed"

register_namespace("torznab", TORZNAB_NS)

SETTINGS_STORE = SettingsStore()
RESULT_CANDIDATE_WINDOW = 1000


def get_conn():
    return psycopg.connect(**DB_CONFIG)


def normalize_imdb(imdbid: str | None):
    if not imdbid:
        return None

    imdbid = imdbid.strip()

    if imdbid.startswith("tt"):
        return imdbid

    return f"tt{imdbid}"


def query_generic(
    q: str | None,
    limit: int,
    offset: int,
):
    with get_conn() as conn:
        with conn.cursor() as cur:

            if not q:
                cur.execute(
                    """
                    SELECT
                        title,
                        size,
                        seeders,
                        provider,
                        upload_date,
                        info_hash,
                        type
                    FROM torrents
                    WHERE size IS NOT NULL
                    ORDER BY seeders DESC NULLS LAST
                    LIMIT %s
                    OFFSET %s
                    """,
                    (
                        limit,
                        offset,
                    ),
                )

            else:
                cur.execute(
                    """
                    SELECT
                        title,
                        size,
                        seeders,
                        provider,
                        upload_date,
                        info_hash,
                        type
                    FROM torrents
                    WHERE title ILIKE %s
                    ORDER BY seeders DESC NULLS LAST
                    LIMIT %s
                    OFFSET %s
                    """,
                    (
                        f"%{q}%",
                        limit,
                        offset,
                    ),
                )

            return cur.fetchall()


def query_movie(
    imdb_id: str | None,
    tmdb_id: int | None,
    q: str | None,
    limit: int,
    offset: int,
):
    with get_conn() as conn:
        with conn.cursor() as cur:

            if imdb_id:
                cur.execute(
                    """
                    SELECT
                        title,
                        size,
                        seeders,
                        provider,
                        upload_date,
                        info_hash,
                        type
                    FROM torrents
                    WHERE type = 'movie'
                      AND imdb_id = %s
                    ORDER BY seeders DESC NULLS LAST
                    LIMIT %s
                    OFFSET %s
                    """,
                    (
                        imdb_id,
                        limit,
                        offset,
                    ),
                )

            elif tmdb_id is not None:
                cur.execute(
                    """
                    SELECT
                        title,
                        size,
                        seeders,
                        provider,
                        upload_date,
                        info_hash,
                        type
                    FROM torrents
                    WHERE type = 'movie'
                      AND tmdb_id = %s
                    ORDER BY seeders DESC NULLS LAST
                    LIMIT %s
                    OFFSET %s
                    """,
                    (
                        tmdb_id,
                        limit,
                        offset,
                    ),
                )

            elif q:
                cur.execute(
                    """
                    SELECT
                        title,
                        size,
                        seeders,
                        provider,
                        upload_date,
                        info_hash,
                        type
                    FROM torrents
                    WHERE type = 'movie'
                      AND title ILIKE %s
                    ORDER BY seeders DESC NULLS LAST
                    LIMIT %s
                    OFFSET %s
                    """,
                    (
                        f"%{q}%",
                        limit,
                        offset,
                    ),
                )

            else:
                return []

            return cur.fetchall()


def query_tv(
    imdb_id: str | None,
    q: str | None,
    season: int | None,
    episode: int | None,
    limit: int,
    offset: int,
):
    with get_conn() as conn:
        with conn.cursor() as cur:

            #
            # 1. Episodio preciso:
            #
            # imdbid + season + episode
            #
            if (
                imdb_id is not None
                and season is not None
                and episode is not None
            ):
                cur.execute(
                    """
                    SELECT
                        title,
                        size,
                        seeders,
                        provider,
                        upload_date,
                        info_hash,
                        type
                    FROM torrents
                    WHERE type IN ('series', 'anime')
                      AND imdb_id = %s
                      AND imdb_season = %s
                      AND imdb_episode = %s
                    ORDER BY seeders DESC NULLS LAST
                    LIMIT %s
                    OFFSET %s
                    """,
                    (
                        imdb_id,
                        season,
                        episode,
                        limit,
                        offset,
                    ),
                )

                return cur.fetchall()

            #
            # 2. Ricerca stagione tramite IMDb:
            #
            # imdbid + season
            #
            if (
                imdb_id is not None
                and season is not None
            ):
                season_sxx = f"S{season:02d}"
                season_word = f"Season {season}"

                cur.execute(
                    """
                    SELECT
                        title,
                        size,
                        seeders,
                        provider,
                        upload_date,
                        info_hash,
                        type
                    FROM torrents
                    WHERE type IN ('series', 'anime')
                      AND imdb_id = %s
                      AND (
                            imdb_season = %s
                            OR (
                                imdb_season IS NULL
                                AND (
                                    title ILIKE %s
                                    OR title ILIKE %s
                                )
                            )
                      )
                    ORDER BY seeders DESC NULLS LAST
                    LIMIT %s
                    OFFSET %s
                    """,
                    (
                        imdb_id,
                        season,
                        f"%{season_sxx}%",
                        f"%{season_word}%",
                        limit,
                        offset,
                    ),
                )

                return cur.fetchall()

            #
            # 3. Ricerca per titolo + stagione:
            #
            # q + season
            #
            if (
                q is not None
                and season is not None
            ):
                season_sxx = f"S{season:02d}"
                season_word = f"Season {season}"

                cur.execute(
                    """
                    SELECT
                        title,
                        size,
                        seeders,
                        provider,
                        upload_date,
                        info_hash,
                        type
                    FROM torrents
                    WHERE type IN ('series', 'anime')
                      AND title ILIKE %s
                      AND (
                            imdb_season = %s
                            OR title ILIKE %s
                            OR title ILIKE %s
                      )
                    ORDER BY seeders DESC NULLS LAST
                    LIMIT %s
                    OFFSET %s
                    """,
                    (
                        f"%{q}%",
                        season,
                        f"%{season_sxx}%",
                        f"%{season_word}%",
                        limit,
                        offset,
                    ),
                )

                return cur.fetchall()

            #
            # 4. Ricerca tramite IMDb senza stagione
            #
            if imdb_id is not None:
                cur.execute(
                    """
                    SELECT
                        title,
                        size,
                        seeders,
                        provider,
                        upload_date,
                        info_hash,
                        type
                    FROM torrents
                    WHERE type IN ('series', 'anime')
                      AND imdb_id = %s
                    ORDER BY seeders DESC NULLS LAST
                    LIMIT %s
                    OFFSET %s
                    """,
                    (
                        imdb_id,
                        limit,
                        offset,
                    ),
                )

                return cur.fetchall()

            #
            # 5. Ricerca generica per titolo
            #
            if q:
                cur.execute(
                    """
                    SELECT
                        title,
                        size,
                        seeders,
                        provider,
                        upload_date,
                        info_hash,
                        type
                    FROM torrents
                    WHERE type IN ('series', 'anime')
                      AND title ILIKE %s
                    ORDER BY seeders DESC NULLS LAST
                    LIMIT %s
                    OFFSET %s
                    """,
                    (
                        f"%{q}%",
                        limit,
                        offset,
                    ),
                )

                return cur.fetchall()

            return []


def make_caps():
    caps = Element("caps")

    server = SubElement(caps, "server")
    server.set("version", "1.0")
    server.set("title", "ICVDB Local Indexer")

    limits = SubElement(caps, "limits")
    limits.set("max", "200")
    limits.set("default", "100")

    searching = SubElement(
        caps,
        "searching",
    )

    search = SubElement(
        searching,
        "search",
    )
    search.set(
        "available",
        "yes",
    )
    search.set(
        "supportedParams",
        "q",
    )

    tv_search = SubElement(
        searching,
        "tv-search",
    )
    tv_search.set(
        "available",
        "yes",
    )
    tv_search.set(
        "supportedParams",
        "q,season,ep,imdbid",
    )

    movie_search = SubElement(
        searching,
        "movie-search",
    )
    movie_search.set(
        "available",
        "yes",
    )
    movie_search.set(
        "supportedParams",
        "q,imdbid,tmdbid",
    )

    categories = SubElement(
        caps,
        "categories",
    )

    movie_cat = SubElement(
        categories,
        "category",
    )
    movie_cat.set(
        "id",
        "2000",
    )
    movie_cat.set(
        "name",
        "Movies",
    )

    tv_cat = SubElement(
        categories,
        "category",
    )
    tv_cat.set(
        "id",
        "5000",
    )
    tv_cat.set(
        "name",
        "TV",
    )

    anime_cat = SubElement(
        categories,
        "category",
    )
    anime_cat.set(
        "id",
        "5070",
    )
    anime_cat.set(
        "name",
        "TV/Anime",
    )

    return tostring(
        caps,
        encoding="utf-8",
        xml_declaration=True,
    )


def category_for_type(torrent_type: str):
    if torrent_type == "movie":
        return 2000

    if torrent_type == "anime":
        return 5070

    return 5000


def make_rss(rows):
    rss = Element(
        "rss",
        {
            "version": "2.0",
        },
    )

    channel = SubElement(
        rss,
        "channel",
    )

    SubElement(
        channel,
        "title",
    ).text = "ICVDB Local Indexer"

    SubElement(
        channel,
        "description",
    ).text = "Local ICVDB Torznab indexer"

    SubElement(
        channel,
        "link",
    ).text = "http://localhost/"

    for row in rows:
        (
            title,
            size,
            seeders,
            provider,
            upload_date,
            info_hash,
            torrent_type,
        ) = row

        category = category_for_type(
            torrent_type
        )

        magnet = (
            f"magnet:?xt=urn:btih:{info_hash}"
        )

        item = SubElement(
            channel,
            "item",
        )

        SubElement(
            item,
            "title",
        ).text = title

        guid = SubElement(
            item,
            "guid",
        )

        guid.set(
            "isPermaLink",
            "false",
        )

        guid.text = info_hash

        SubElement(
            item,
            "link",
        ).text = magnet

        if upload_date:
            SubElement(
                item,
                "pubDate",
            ).text = upload_date.strftime(
                "%a, %d %b %Y %H:%M:%S +0000"
            )

        enclosure = SubElement(
            item,
            "enclosure",
        )

        enclosure.set(
            "url",
            magnet,
        )

        enclosure.set(
            "type",
            "application/x-bittorrent",
        )

        if size is not None:
            enclosure.set(
                "length",
                str(size),
            )

        def attr(name, value):
            if value is None:
                return

            element = SubElement(
                item,
                f"{{{TORZNAB_NS}}}attr",
            )

            element.set(
                "name",
                name,
            )

            element.set(
                "value",
                str(value),
            )

        attr(
            "category",
            category,
        )

        attr(
            "infohash",
            info_hash,
        )

        attr(
            "magneturl",
            magnet,
        )

        attr(
            "seeders",
            seeders or 0,
        )

        attr(
            "peers",
            seeders or 0,
        )

        if size is not None:
            attr(
                "size",
                size,
            )

        attr(
            "downloadvolumefactor",
            0,
        )

        attr(
            "uploadvolumefactor",
            1,
        )

        if provider:
            attr(
                "description",
                provider,
            )

    return tostring(
        rss,
        encoding="utf-8",
        xml_declaration=True,
    )


def query_processed(query, query_args, limit, offset):
    processing = SETTINGS_STORE.load()["result_processing"]
    if processing["preset"] == "unfiltered":
        return query(*query_args, limit, offset)

    # Rank within fixed, non-overlapping database windows. This keeps memory
    # bounded, supports arbitrary offsets, and fetches both windows when a page
    # crosses a boundary; ranking intentionally remains local to each window.
    request_end = offset + limit
    first_window = (offset // RESULT_CANDIDATE_WINDOW) * RESULT_CANDIDATE_WINDOW
    last_window = (
        (request_end - 1) // RESULT_CANDIDATE_WINDOW
    ) * RESULT_CANDIDATE_WINDOW
    page = []
    for window_offset in range(
        first_window,
        last_window + RESULT_CANDIDATE_WINDOW,
        RESULT_CANDIDATE_WINDOW,
    ):
        rows = query(*query_args, RESULT_CANDIDATE_WINDOW, window_offset)
        processed = process_results(
            rows,
            processing["preset"],
            processing["custom_rules"],
        )
        local_start = max(offset - window_offset, 0)
        local_end = min(request_end - window_offset, RESULT_CANDIDATE_WINDOW)
        page.extend(processed[local_start:local_end])
    return page


@app.get("/api")
def torznab(
    t: str = Query("search"),
    q: str | None = None,
    imdbid: str | None = None,
    tmdbid: int | None = None,
    season: int | None = None,
    ep: int | None = None,
    cat: str | None = None,
    limit: int = Query(
        100,
        ge=1,
        le=200,
    ),
    offset: int = Query(
        0,
        ge=0,
    ),
    apikey: str | None = None,
    extended: int | None = None,
):
    if t == "caps":
        return Response(
            content=make_caps(),
            media_type="application/xml",
        )

    imdb_id = normalize_imdb(
        imdbid
    )

    if t == "search":
        rows = query_processed(
            query_generic,
            (q,),
            limit,
            offset,
        )

        return Response(
            content=make_rss(rows),
            media_type="application/xml",
        )

    if t == "movie":
        rows = query_processed(
            query_movie,
            (imdb_id, tmdbid, q),
            limit,
            offset,
        )

        return Response(
            content=make_rss(rows),
            media_type="application/xml",
        )

    if t == "tvsearch":
        rows = query_processed(
            query_tv,
            (imdb_id, q, season, ep),
            limit,
            offset,
        )

        return Response(
            content=make_rss(rows),
            media_type="application/xml",
        )

    return Response(
        content=make_rss([]),
        media_type="application/xml",
    )
