from http import HTTPStatus

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from requests.exceptions import HTTPError
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

# TODO: Rename them to plural form for consistency e.g. 'tests' instead of 'test'
from project.settings import CHROME_OPTIONS
from core.test.utils import stub_request, stub_request_exception, mock_response
from core.test.mixins import CustomAssertionsMixin
from oauth.tests.utils import selenium_sign_in_user
from movie_loggers.services.trakt import Trakt
from movies.models import Movie
from movie_loggers.services.base import MovieLogger
from movies.tests.utils import create_dummy_movie

class TraktSystemTestCase(StaticLiveServerTestCase, CustomAssertionsMixin):
    fixtures = ["movies.json", "countries.json"]

    def setUp(self):
        self.movie = Movie.objects.get(pk=1)
        for _ in range(4):
            create_dummy_movie(self.movie)
        self.selenium = webdriver.Chrome(CHROME_OPTIONS)
        self.selenium.implicitly_wait(10)

    def tearDown(self):
        self.selenium.quit()
        super().tearDownClass()

    def test_adding_to_watchlist_success(self):
        selenium_sign_in_user(self, MovieLogger.TRAKT.value)
        url = reverse("movies:index")
        self.selenium.get(f"{self.live_server_url}/{url}")
        mocked_response = {
            "body": {"not_found": {"movies": []}},
        }
        message = f"'{self.movie.title}' has been added to Trakt's watchlist."
        with stub_request(Trakt, response=mocked_response):
            self.selenium.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            self.assertJsFlashMessage(message)

    def test_adding_to_watchlist_movie_not_found(self):
        selenium_sign_in_user(self, MovieLogger.TRAKT.value)
        url = reverse("movies:index")
        self.selenium.get(f"{self.live_server_url}/{url}")
        mocked_response = {
            "body": {"not_found": {"movies": [
                {"ids": {"imdb": self.movie.imdb_id}}
            ]}},
        }
        message = f"Trakt couldn't find '{self.movie.title}'."
        with stub_request(Trakt, response=mocked_response):
            self.selenium.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            self.assertJsFlashMessage(message)

    def test_account_is_locked(self):
        selenium_sign_in_user(self, MovieLogger.TRAKT.value)
        url = reverse("movies:index")
        self.selenium.get(f"{self.live_server_url}/{url}")
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
        with stub_request_exception(Trakt, exception=exception):
            self.selenium.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            self.assertJsFlashMessage(message)

    def test_account_is_deactivated(self):
        selenium_sign_in_user(self, MovieLogger.TRAKT.value)
        url = reverse("movies:index")
        self.selenium.get(f"{self.live_server_url}/{url}")
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
        with stub_request_exception(Trakt, exception=exception):
            self.selenium.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            self.assertJsFlashMessage(message)

    def test_vip_account_reached_limit(self):
        selenium_sign_in_user(self, MovieLogger.TRAKT.value)
        url = reverse("movies:index")
        self.selenium.get(f"{self.live_server_url}/{url}")
        mocked_response = {
            "body": {},
            "status_code": Trakt.HTTP_STATUS_CODE_VIP_ENHANCED,
            "headers": {
                "X-Upgrade-URL": Trakt.VIP_UPGRADE_URL,
                "X-VIP-User": "true",
            }
        }
        exception = HTTPError(response=mock_response(mocked_response))
        message = "You have reached limit for your Trakt account."
        with stub_request_exception(Trakt, exception=exception):
            self.selenium.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            self.assertJsFlashMessage(message)
