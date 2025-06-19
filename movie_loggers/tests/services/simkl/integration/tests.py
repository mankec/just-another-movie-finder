from time import time as unix_time
from unittest import skip

from django.test import TestCase, Client
from django.urls import reverse

from core.test.utils import stub_request
from core.test.mixins import CustomAssertionsMixin
from movie_loggers.services.simkl import Simkl
from movies.models import Movie
from movie_loggers.services.base import MovieLogger

class SimklIntegrationTestCase(TestCase, CustomAssertionsMixin):
    fixtures = ["movies.json"]

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

    @skip("This requires system test")
    def test_adding_to_watchlist_success(self):
        url = reverse("movies:add_to_watchlist", kwargs={"movie_id": self.movie.tvdb_id})
        mocked_response = {
            "body": {"not_found": {"movies": []}},
        }
        message = f"'{self.movie.title}' has been added to your Simkl's watchlist."
        with stub_request(self.simkl, response=mocked_response):
            response = self.client.post(url)
            self.assertFlashMessage(response, message)

    @skip("This requires system test")
    def test_adding_to_watchlist_movie_not_found(self):
        url = reverse("movies:add_to_watchlist", kwargs={"movie_id": self.movie.tvdb_id})
        mocked_response = {
            "body": {"not_found": {"movies": [
                {"ids": {"imdb": self.movie.imdb_id}}
            ]}},
        }
        message = f"Simkl couldn't find '{self.movie.title}'."
        with stub_request(self.simkl, response=mocked_response):
            response = self.client.post(url)
            self.assertFlashMessage(response, message)
