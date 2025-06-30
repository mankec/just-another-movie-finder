from time import time as unix_time
from unittest import skipIf

from requests.exceptions import HTTPError
from django.test import TestCase, Client
from django.urls import reverse

from project.settings import SKIP_EXTERNAL_TESTS
from core.sessions.utils import initialize_session
from core.constants import ONE_DAY_IN_SECONDS
from core.tests.utils import stub_request, stub_request_exception, mock_response
from core.tests.mixins import CustomAssertionsMixin
from movie_loggers.services.trakt.services import Trakt
from movies.models import Movie
from movie_loggers.services.base import MovieLogger

class TraktIntegrationTestCase(TestCase, CustomAssertionsMixin):
    fixtures = ["movies.json", "countries.json"]

    def setUp(self):
        self.client = Client()
        session = self.client.session
        initialize_session(session)
        session.save()
        self.trakt = Trakt("")
        self.movie = Movie.objects.get(pk=1)

    def test_signing_in(self):
        session = self.client.session
        session["movie_logger"] =MovieLogger.TRAKT.value
        session.save()
        token = "token"
        refresh_token = "refresh_token"
        token_expires_at = int(unix_time())
        mocked_response = {
            "body": {
                "access_token": token,
                "refresh_token":refresh_token,
                "created_at": token_expires_at,
            }
        }
        message = "Successfully signed with Trakt!"
        url = reverse("oauth:index")
        with stub_request(self.trakt, response=mocked_response):
            response = self.client.get(url, query_params={"code": "code"}, follow=True)
            session = self.client.session
            self.assertFlashMessage(response, message)
            self.assertEqual(session["token"], token)
            self.assertEqual(session["refresh_token"], refresh_token)
            self.assertEqual(
                session["token_expires_at"],
                token_expires_at + ONE_DAY_IN_SECONDS
            )

    @skipIf(SKIP_EXTERNAL_TESTS.value, SKIP_EXTERNAL_TESTS.reason)
    def test_account_requires_vip_upgrade(self):
        session = self.client.session
        session["movie_logger"] =MovieLogger.TRAKT.value
        session["token"] = "token"
        session.save()
        url = reverse("movies:add_to_watchlist", kwargs={"movie_id": self.movie.tvdb_id})
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
