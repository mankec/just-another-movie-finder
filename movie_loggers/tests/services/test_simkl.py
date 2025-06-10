from unittest.mock import patch

from django.test import TestCase
from django.contrib.sessions.backends.db import SessionStore

from movie_loggers.services.simkl import Simkl
from project.utils.testing_utils import stub_request


class SimklTestCase(TestCase):
    def setUp(self):
        self.session = SessionStore()
        self.session["movie_logger_name"] = "simkl"
        self.session["token"] = ""
        self.session.create()
        self.movie_logger = Simkl(self.session)
        self.klass = self.movie_logger.__class__

    def test_authorizing_application(self):
        code = "code"
        response = {"body":
            {"access_token": "mocked_token"}
        }

        with stub_request(self.movie_logger, response=response):
            self.movie_logger.exchange_code_and_save_token(code)

    def test_adding_movie_to_watchlist(self):
        movie_id = 41834
        movie = {
            "id": movie_id,
        }
        movie_data = {
            "ids": {
                "tvdb": movie_id,
            }
        }
        response = {"body":
            {'added': {
                'movies': [
                    {'type': 'movie', 'title': 'Frozen Stiff', 'poster': '99/9914076e60318349c', 'year': 2002, 'status': 'released', 'ids': {'simkl': 71106, 'slug': 'frozen-stiff', 'tvdb': movie_id}, 'to': 'plantowatch'
                    }
                ], 'shows': []}, 'not_found': {'movies': [], 'shows': []}
            }
        }

        with stub_request(self.movie_logger, response=response):
            with patch(
                f"{self.klass.__module__}.{self.klass.__name__}._fetch_movie",
                return_value=movie_data
            ):
                self.movie_logger.add_to_watchlist(movie)
