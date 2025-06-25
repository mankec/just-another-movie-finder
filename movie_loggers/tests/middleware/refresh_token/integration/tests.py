from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.test import TestCase, Client
from freezegun import freeze_time

from core.tests.utils import stub_request
from core.sessions.utils import initialize_session
from project.settings import TIME_ZONE
from movie_loggers.tests.services.constants import DEFAULT_TEST_MOVIE_LOGGER
from movie_loggers.services.creator import MovieLoggerCreator

class RefreshTokenMiddlewareIntegrationTestCase(TestCase):
    def test_refreshing_access_token(self):
        client = Client()
        refresh_token_1 = "refresh_token_1"
        refresh_token_2 = "refresh_token_2"
        time_zone = ZoneInfo(TIME_ZONE)
        tomorrow = datetime.now(time_zone) + timedelta(days=1)
        mocked_response = {
            "body": {
                "access_token": "token",
                "refresh_token": refresh_token_2,
                "created_at": int(tomorrow.timestamp()),
            }
        }
        session = client.session
        initialize_session(session)
        session["movie_logger"] = DEFAULT_TEST_MOVIE_LOGGER
        session["refresh_token"] = refresh_token_1
        session["token_expires_at"] = int(tomorrow.timestamp())
        session.save()
        movie_logger = MovieLoggerCreator(session)

        client.get("/")
        self.assertEqual(session["refresh_token"], refresh_token_1)

        with freeze_time(tomorrow):
            with stub_request(movie_logger, response=mocked_response):
                client.get("/")
                self.assertEqual(client.session["refresh_token"], refresh_token_2)
