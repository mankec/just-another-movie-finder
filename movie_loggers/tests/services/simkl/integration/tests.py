from django.test import TestCase, Client
from django.urls import reverse

from core.tests.utils import stub_request
from core.tests.mixins import CustomAssertionsMixin
from core.sessions.utils import initialize_session
from movie_loggers.services.simkl.services import Simkl
from movies.models import Movie
from movie_loggers.services.base import MovieLogger

class SimklIntegrationTestCase(TestCase, CustomAssertionsMixin):
    fixtures = ["movies.json", "countries.json"]

    def test_signing_in(self):
        client = Client()
        session = client.session
        initialize_session(session)
        session["movie_logger"] = MovieLogger.SIMKL.value
        session.save()
        simkl = Simkl("")

        token = "token"
        mocked_response = {
            "body": {
                "access_token": token,
            }
        }
        message = "Successfully signed with Simkl!"
        url = reverse("oauth:index")
        with stub_request(simkl, response=mocked_response):
            response = client.get(url, query_params={"code": "code"}, follow=True)
            session = client.session
            self.assertFlashMessage(response, message)
            self.assertEqual(session["token"], token)
