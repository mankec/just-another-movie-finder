from django.test import TestCase
from django.contrib.sessions.backends.db import SessionStore

from core.tests.utils import stub_multiple_requests
from movie_loggers.services.trakt.services import Trakt
from movie_loggers.services.base import MovieLogger

class TraktUnitTestCase(TestCase):

    def test_fetching_user_watchlist(self):
        session = SessionStore()
        session["movie_logger"] = MovieLogger.TRAKT.value
        session["token"] = "token"
        session.create()
        trakt = Trakt(session)

        total_pages = 2
        imdb_id_1 = "imdb_id_1"
        tmdb_id_1 = "tmdb_id_1"
        imdb_id_2 = "tmdb_id_2"
        tmdb_id_2 = "tmdb_id_2"
        responses = [
            {
                "body": [
                    {
                        "movie": {
                            "ids": {
                                "imdb": imdb_id_1,
                                "tmdb": tmdb_id_1,
                            }
                        }
                    }
                ],
                "headers": { "X-Pagination-Page-Count": total_pages }
            },
            {
                "body": [
                    {
                        "movie": {
                            "ids": {
                                "imdb": imdb_id_2,
                                "tmdb": tmdb_id_2,
                            }
                        }
                    }
                ],
                "headers": { "X-Pagination-Page-Count": total_pages }
            },
        ]
        expected = [
            { "imdb_id": imdb_id_1, "tmdb_id": tmdb_id_1 },
            { "imdb_id": imdb_id_2, "tmdb_id": tmdb_id_2 },
        ]
        with stub_multiple_requests(trakt, responses=responses):
            movie_ids = trakt.fetch_movie_ids_in_watchlist()
            self.assertEqual(movie_ids, expected)
