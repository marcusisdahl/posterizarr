"""Pure helpers for the Posterizarr/Agregarr integration."""


def build_arr_trigger_maps(payload, event_type):
    """Return the Arr platform and one Posterizarr trigger map per media item."""
    data_map = {}

    if "movie" in payload:
        movie = payload.get("movie", {})
        movie_file = payload.get("movieFile", {})
        data_map.update(
            {
                "arr_platform": "Radarr",
                "event": event_type,
                "arr_movie_title": movie.get("title", ""),
                "arr_movie_tmdb": movie.get("tmdbId", ""),
                "arr_movie_imdb": movie.get("imdbId", ""),
                "arr_movie_year": movie.get("year", ""),
                "arr_movie_path": movie.get("folderPath", ""),
            }
        )
        if movie_file:
            data_map["arr_moviefile_path"] = movie_file.get("path", "")
            data_map["arr_moviefile_id"] = movie_file.get("id", "")
        return "Radarr", [data_map]

    if "series" in payload:
        series = payload.get("series", {})
        episodes = payload.get("episodes", [])
        data_map.update(
            {
                "arr_platform": "Sonarr",
                "event": event_type,
                "arr_series_title": series.get("title", ""),
                "arr_series_tvdb": series.get("tvdbId", ""),
                "arr_series_path": series.get("path", ""),
            }
        )
        if "imdbId" in series:
            data_map["arr_series_imdb"] = series.get("imdbId")

        if not episodes:
            if "episodeFile" in payload:
                data_map["arr_episode_path"] = payload["episodeFile"].get(
                    "path", ""
                )
            return "Sonarr", [data_map]

        trigger_maps = []
        for episode in episodes:
            episode_map = dict(data_map)
            episode_map["arr_episode_season"] = episode.get("seasonNumber", "")
            episode_map["arr_episode_numbers"] = episode.get("episodeNumber", "")
            episode_map["arr_episode_titles"] = episode.get("title", "")
            if "episodeFile" in payload:
                episode_map["arr_episode_path"] = payload["episodeFile"].get(
                    "path", ""
                )
            trigger_maps.append(episode_map)
        return "Sonarr", trigger_maps

    raise ValueError("Unknown Arr payload format")


def classify_agregarr_validation_response(status_code, payload=None):
    """Convert an Agregarr status response into the Web UI validation result."""
    payload = payload if isinstance(payload, dict) else {}

    if status_code == 200:
        return {
            "valid": True,
            "message": "Agregarr connection and API key are valid.",
            "details": {"status_code": 200},
        }

    if status_code == 403 and "integration is disabled" in str(
        payload.get("error", "")
    ).lower():
        return {
            "valid": False,
            "message": "Agregarr is reachable, but its Posterizarr integration is disabled. Enable it in Agregarr's Overlay Settings.",
            "details": {"status_code": 403, "error": "integration_disabled"},
        }

    if status_code in (401, 403):
        return {
            "valid": False,
            "message": "Agregarr rejected the API key.",
            "details": {"status_code": status_code},
        }

    if status_code == 404:
        return {
            "valid": False,
            "message": "Agregarr is reachable, but its Posterizarr integration endpoint is unavailable.",
            "details": {"status_code": 404},
        }

    return {
        "valid": False,
        "message": f"Agregarr connection failed (Status: {status_code}).",
        "details": {"status_code": status_code},
    }
