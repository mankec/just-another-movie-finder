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
        session = self.client.session
        initialize_session(session)
        session["movie_logger"] = MovieLogger.SIMKL.value
        session.save()
        self.simkl = Simkl(session)
        self.movie = Movie.objects.get(pk=1)

        mocked_response = {
            "body": {
                "access_token": "token",
            }
        }
        message = "Successfully signed with Simkl!"
        url = reverse("oauth:index")
        with stub_request(self.simkl, response=mocked_response):
            response = self.client.get(url, query_params={"code": "code"}, follow=True)
            self.assertFlashMessage(response, message)
