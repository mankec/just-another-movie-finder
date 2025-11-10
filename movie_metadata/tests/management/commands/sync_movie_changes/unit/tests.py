import ast
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from core.tests.utils import stub_requests, mock_response
from core.constants import TMDB_ACTIONS
from movie_metadata.services import MovieMetadata
from movies.models import Movie, Genre

class SyncMovieChangesTest(TestCase):
    fixtures = ["movies.json", "genres.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fetch_latest_movie_id_patcher = patch('movie_metadata.services.MovieMetadata.TMDB._fetch_latest_movie_id', return_value=2)
        cls.mock_fetch_latest_movie_id = cls.fetch_latest_movie_id_patcher.start()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.fetch_latest_movie_id_patcher.stop()

    def setUp(self):
        self.tmdb = MovieMetadata.TMDB()
        self.movie = Movie.objects.get(id=1)
        self.movie_changes_response = {
            "body": {
                "results": [
                    {
                        "id": self.movie.id,
                        "adult": False
                    }
                ],
                "page": 1,
                "total_pages": 1,
            }
        }
        self.new_poster_1_path = "/new_poster_1.jpg"
        self.new_poster_2_path = "/new_poster_2.jpg"
        self.poster_1_path = "/poster_1.jpg"
        self.poster_2_path = "/poster_2.jpg"

    def test_genres_added(self):
        genre_1 = Genre.objects.get(pk=27)
        genre_2 = Genre.objects.get(pk=28)
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "genres",
                            "items": [
                                {
                                    "id": "691520e8535cb85e69ac20e3",
                                    "action": "added",
                                    "time": "2025-11-13 00:06:00 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "value": {
                                        "name": genre_1.name,
                                        "id": genre_1.id
                                    }
                                },
                                {
                                    "id": "691520ed2f9649b50a4c960a",
                                    "action": "added",
                                    "time": "2025-11-13 00:06:05 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "value": {
                                        "name": genre_1.name,
                                        "id": genre_2.id
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.movie.refresh_from_db()
            genre_names = list(self.movie.genres.all().order_by("id").values_list("name", flat=True))
            expected = [genre_1.name, genre_2.name]
            self.assertEqual(genre_names, expected)

    def test_poster_images_added(self):
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "images",
                            "items": [
                                {
                                    "id": "6915249feba221c4a93a3f0c",
                                    "action": TMDB_ACTIONS["added"],
                                    "time": "2025-11-13 00:21:51 UTC",
                                    "iso_639_1": "es",
                                    "iso_3166_1": "MX",
                                    "value": {
                                        "poster": {
                                        "file_path": self.new_poster_1_path,
                                        "iso_639_1": "es",
                                        "iso_3166_1": "MX"
                                        }
                                    },
                                },
                                {
                                    "id": "691524a66e28e62421876478",
                                    "action": TMDB_ACTIONS["added"],
                                    "time": "2025-11-13 00:21:58 UTC",
                                    "iso_639_1": "es",
                                    "iso_3166_1": "MX",
                                    "value": {
                                        "poster": {
                                        "file_path": self.new_poster_2_path,
                                        "iso_639_1": "es",
                                        "iso_3166_1": "MX"
                                        }
                                    },
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.movie.refresh_from_db()
            posters = list(map(ast.literal_eval, self.movie.posters))
            expected = [self.poster_1_path, self.poster_2_path, self.new_poster_1_path,self. new_poster_2_path]
            poster_paths = [x["file_path"] for x in posters]
            self.assertEqual(poster_paths, expected)

    def test_poster_images_updated(self):
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "images",
                            "items": [
                                {
                                    "id": "6915249feba221c4a93a3f0c",
                                    "action": TMDB_ACTIONS["updated"],
                                    "time": "2025-11-13 00:21:51 UTC",
                                    "iso_639_1": "es",
                                    "iso_3166_1": "MX",
                                    "value": {
                                        "poster": {
                                        "file_path": self.new_poster_1_path,
                                        "iso_639_1": "es",
                                        "iso_3166_1": "MX"
                                        }
                                    },
                                    "original_value": {
                                        "poster": {
                                        "file_path": self.poster_1_path,
                                        "iso_639_1": "es",
                                        "iso_3166_1": "ES"
                                        }
                                    }
                                },
                                {
                                    "id": "691524a66e28e62421876478",
                                    "action": TMDB_ACTIONS["updated"],
                                    "time": "2025-11-13 00:21:58 UTC",
                                    "iso_639_1": "es",
                                    "iso_3166_1": "MX",
                                    "value": {
                                        "poster": {
                                        "file_path": self.new_poster_2_path,
                                        "iso_639_1": "es",
                                        "iso_3166_1": "MX"
                                        }
                                    },
                                    "original_value": {
                                        "poster": {
                                        "file_path": self.poster_2_path,
                                        "iso_639_1": "es",
                                        "iso_3166_1": "ES"
                                        }
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.movie.refresh_from_db()
            posters = list(map(ast.literal_eval, self.movie.posters))
            expected = [self.new_poster_1_path, self.new_poster_2_path]
            poster_paths = [x["file_path"] for x in posters]
            self.assertEqual(poster_paths, expected)

    def test_poster_images_deleted(self):
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "images",
                            "items": [
                                {
                                    "id": "6915249feba221c4a93a3f0c",
                                    "action": TMDB_ACTIONS["deleted"],
                                    "time": "2025-11-13 00:21:51 UTC",
                                    "iso_639_1": "es",
                                    "iso_3166_1": "MX",
                                    "original_value": {
                                        "poster": {
                                        "file_path": self.poster_1_path,
                                        "iso_639_1": "es",
                                        "iso_3166_1": "MX"
                                        }
                                    },
                                },
                                {
                                    "id": "691524a66e28e62421876478",
                                    "action": TMDB_ACTIONS["deleted"],
                                    "time": "2025-11-13 00:21:58 UTC",
                                    "iso_639_1": "es",
                                    "iso_3166_1": "MX",
                                    "original_value": {
                                        "poster": {
                                        "file_path": self.poster_2_path,
                                        "iso_639_1": "es",
                                        "iso_3166_1": "MX"
                                        }
                                    },
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.movie.refresh_from_db()
            posters = list(map(ast.literal_eval, self.movie.posters))
            expected = []
            poster_paths = [x["file_path"] for x in posters]
            self.assertEqual(poster_paths, expected)
