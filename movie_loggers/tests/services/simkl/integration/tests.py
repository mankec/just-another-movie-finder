from django.test import TestCase, Client
from django.urls import reverse

from core.tests.utils import stub_request
from core.tests.mixins import CustomAssertionsMixin
from movie_loggers.services.simkl import Simkl
from movies.models import Movie
from movie_loggers.services.base import MovieLogger

class SimklIntegrationTestCase(TestCase, CustomAssertionsMixin):
    fixtures = ["movies.json", "countries.json"]

    def setUp(self):
        self.client = Client()
        session = self.client.session
        session["movie_logger"] =MovieLogger.SIMKL.value
        session["token"] = "token"
        session.save()
        self.simkl = Simkl(session)
        self.movie = Movie.objects.get(pk=1)

    def test_signing_in(self):
        session = self.client.session
        del session["token"]
        session.save()

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
