from django.test import TestCase
from django.contrib.sessions.backends.db import SessionStore

from core.tests.utils import stub_multiple_requests
from movie_loggers.services.simkl import Simkl
from movie_loggers.services.base import MovieLogger


class SimklUnitTestCase(TestCase):

    def test_fetching_user_watchlist(self):
        session = SessionStore()
        session["movie_logger"] = MovieLogger.SIMKL.value
        session["token"] = "token"
        session.create()
        simkl = Simkl(session)

        imdb_id_1 = "imdb_id_1"
        tmdb_id_1 = "tmdb_id_1"
        imdb_id_2 = "tmdb_id_2"
        tmdb_id_2 = "tmdb_id_2"
        responses = [
            {
                "body": {
                    "movies": [
                        {
                            "movie": {
                                "ids": {
                                    "imdb": imdb_id_1,
                                    "tmdb": tmdb_id_1,
                                }
                            }
                        },
                        {
                            "movie": {
                                "ids": {
                                    "imdb": imdb_id_2,
                                    "tmdb": tmdb_id_2,
                                }
                            }
                        },
                    ]
                },
            },
        ]
        expected = [
            { "imdb_id": imdb_id_1, "tmdb_id": tmdb_id_1 },
            { "imdb_id": imdb_id_2, "tmdb_id": tmdb_id_2 },
        ]
        with stub_multiple_requests(simkl, responses=responses):
            movie_ids = simkl.fetch_movie_ids_in_watchlist()
            self.assertEqual(movie_ids, expected)
