import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "webui" / "backend"))

from agregarr_integration import (  # noqa: E402
    build_arr_trigger_maps,
    classify_agregarr_validation_response,
)


class AgregarrIntegrationTests(unittest.TestCase):
    def test_maps_radarr_download_without_losing_file_identity(self):
        platform, triggers = build_arr_trigger_maps(
            {
                "movie": {
                    "title": "Example Movie",
                    "tmdbId": 456,
                    "imdbId": "tt1234567",
                    "year": 2026,
                    "folderPath": "/movies/example",
                },
                "movieFile": {"id": 99, "path": "/movies/example/movie.mkv"},
            },
            "Download",
        )

        self.assertEqual(platform, "Radarr")
        self.assertEqual(len(triggers), 1)
        self.assertEqual(triggers[0]["arr_movie_tmdb"], 456)
        self.assertEqual(triggers[0]["arr_moviefile_id"], 99)
        self.assertEqual(
            triggers[0]["arr_moviefile_path"], "/movies/example/movie.mkv"
        )

    def test_expands_multi_episode_sonarr_events(self):
        platform, triggers = build_arr_trigger_maps(
            {
                "series": {"title": "Example", "tvdbId": 123, "path": "/tv/example"},
                "episodes": [
                    {"seasonNumber": 1, "episodeNumber": 1, "title": "One"},
                    {"seasonNumber": 1, "episodeNumber": 2, "title": "Two"},
                ],
                "episodeFile": {"path": "/tv/example/S01E01-E02.mkv"},
            },
            "Download",
        )

        self.assertEqual(platform, "Sonarr")
        self.assertEqual([item["arr_episode_numbers"] for item in triggers], [1, 2])
        self.assertTrue(
            all(
                item["arr_episode_path"] == "/tv/example/S01E01-E02.mkv"
                for item in triggers
            )
        )

    def test_distinguishes_disabled_integration_from_bad_key(self):
        disabled = classify_agregarr_validation_response(
            403, {"error": "Posterizarr integration is disabled in Agregarr settings"}
        )
        rejected = classify_agregarr_validation_response(403, {"error": "Forbidden"})

        self.assertEqual(disabled["details"]["error"], "integration_disabled")
        self.assertIn("disabled", disabled["message"])
        self.assertNotIn("integration_disabled", rejected["details"])

    def test_rejects_unknown_arr_payloads(self):
        with self.assertRaises(ValueError):
            build_arr_trigger_maps({"eventType": "Download"}, "Download")


if __name__ == "__main__":
    unittest.main()
