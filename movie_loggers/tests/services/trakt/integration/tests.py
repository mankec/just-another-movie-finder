from time import time as unix_time
from http import HTTPStatus
from unittest import skipIf

from django.test import TestCase, Client
from django.urls import reverse
from requests.exceptions import HTTPError

from project.settings import SKIP_EXTERNAL_TESTS
from core.test.utils import stub_request, stub_request_exception, mock_response
from core.test.mixins import CustomAssertionsMixin
from movie_loggers.services.trakt import Trakt
from movies.models import Movie
from movie_loggers.services.base import MovieLogger

class TraktIntegrationTestCase(TestCase, CustomAssertionsMixin):
    fixtures = ["movies.json"]

    def setUp(self):
        self.client = Client()
        session = self.client.session
        session["movie_logger"] =MovieLogger.TRAKT.value
        session["token"] = "token"
        session.save()
        self.trakt = Trakt(session)
        self.movie = Movie.objects.get(pk=1)

    def test_signing_in(self):
        session = self.client.session
        del session["token"]
        session.save()

        mocked_response = {
            "body": {
                "access_token": "token",
                "refresh_token": "refresh_token",
                "created_at": int(unix_time()),
            }
        }
        message = "Successfully signed with Trakt!"
        url = reverse("auth:index")
        with stub_request(self.trakt, response=mocked_response):
            response = self.client.get(url, query_params={"code": "code"}, follow=True)
            self.assertFlashMessage(response, message)

    def test_adding_to_watchlist_success(self):
        url = reverse("movies:add_to_watchlist", kwargs={"movie_id": self.movie.id})
        mocked_response = {
            "body": {"not_found": {"movies": []}},
            "status_code": HTTPStatus.CREATED.value
        }
        message = f"'{self.movie.title}' has been added to your Trakt's watchlist."
        with stub_request(self.trakt, response=mocked_response):
            response = self.client.post(url)
            self.assertFlashMessage(response, message)

    def test_adding_to_watchlist_movie_not_found(self):
        url = reverse("movies:add_to_watchlist", kwargs={"movie_id": self.movie.id})
        mocked_response = {
            "body": {"not_found": {"movies": [
                {"ids": {"imdb": self.movie.imdb_id}}
            ]}},
        }
        message = f"Trakt couldn't find '{self.movie.title}'."
        with stub_request(self.trakt, response=mocked_response):
            response = self.client.post(url)
            self.assertFlashMessage(response, message)

    def test_account_is_locked(self):
        url = reverse("movies:add_to_watchlist", kwargs={"movie_id": self.movie.id})
        mocked_response = {
            "body": {},
            "status_code": HTTPStatus.LOCKED.value,
            "headers": {
                "X-Account-Locked": "true",
                "X-Account-Deactivated": "false",
            }
        }
        exception = HTTPError(
            HTTPStatus.LOCKED.phrase,
            response=mock_response(mocked_response)
        )
        message = "Your Trakt account is locked. Please contact their support at support@trakt.tv."
        with stub_request_exception(self.trakt, exception=exception):
            response = self.client.post(url)
            self.assertFlashMessage(response, message)

    def test_account_is_deactivated(self):
        url = reverse("movies:add_to_watchlist", kwargs={"movie_id": self.movie.id})
        mocked_response = {
            "body": {},
            "status_code": HTTPStatus.LOCKED.value,
            "headers": {
                "X-Account-Locked": "false",
                "X-Account-Deactivated": "true",
            }
        }
        exception = HTTPError(
            HTTPStatus.LOCKED.phrase,
            response=mock_response(mocked_response)
        )
        message = "Your Trakt account is deactivated. Please contact their support at support@trakt.tv."
        with stub_request_exception(self.trakt, exception=exception):
            response = self.client.post(url)
            self.assertFlashMessage(response, message)

    @skipIf(SKIP_EXTERNAL_TESTS.value, SKIP_EXTERNAL_TESTS.reason)
    def test_account_requires_vip_upgrade(self):
        url = reverse("movies:add_to_watchlist", kwargs={"movie_id": self.movie.id})
        mocked_response = {
            "body": {},
            "status_code": self.trakt.HTTP_STATUS_CODE_VIP_ENHANCED,
            "headers": {
                "X-Upgrade-URL": self.trakt.VIP_UPGRADE_URL,
                "X-VIP-User": "false",
            }
        }
        exception = HTTPError(response=mock_response(mocked_response))
        with stub_request_exception(self.trakt, exception=exception):
            response = self.client.post(url)
            self.assertRedirects(
                response,
                self.trakt.VIP_UPGRADE_URL,
                fetch_redirect_response=False
            )

    def test_vip_account_reached_limit(self):
        url = reverse("movies:add_to_watchlist", kwargs={"movie_id": self.movie.id})
        mocked_response = {
            "body": {},
            "status_code": self.trakt.HTTP_STATUS_CODE_VIP_ENHANCED,
            "headers": {
                "X-Upgrade-URL": self.trakt.VIP_UPGRADE_URL,
                "X-VIP-User": "true",
            }
        }
        self.client.get("/")
        exception = HTTPError(response=mock_response(mocked_response))
        message = "You have reached limit for your Trakt account."
        with stub_request_exception(self.trakt, exception=exception):
            response = self.client.post(url)
            self.assertFlashMessage(response, message)
