from django.test import TestCase, Client
from django.urls import reverse

from core.tests.utils import stub_requests
from core.tests.mixins import CustomAssertionsMixin
from core.sessions.utils import initialize_session
from movie_loggers.services.tmdb.services import TMDB
from movie_loggers.services.base import MovieLogger

class TMDBIntegrationTestCase(TestCase, CustomAssertionsMixin):
    fixtures = ["movies.json", "countries.json"]

    def test_signing_in(self):
        client = Client()
        session = client.session
        initialize_session(session)
        session["movie_logger"] = MovieLogger.TMDB.value
        session.save()
        tmdb = TMDB("")

        request_token = "request_token"
        token = "token"
        mocked_responses = [
            {
                "body": {
                    "session_id": token,
                }
            },
        ]
        message = "Successfully signed with TMDB!"
        url = reverse("oauth:index")
        with stub_requests(tmdb, responses=mocked_responses):
            response = client.get(url, query_params={"request_token": request_token}, follow=True)
            session = client.session
            self.assertFlashMessage(response, message)
            self.assertEqual(session["token"], token)
