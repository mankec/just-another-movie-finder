from http import HTTPStatus

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from requests.exceptions import HTTPError
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

from project.settings import CHROME_OPTIONS
from core.tests.utils import (
    stub_request,
    stub_request_exception,
    mock_response,
    selenium_sign_in_user,
    fill_and_submit_movie_finder_form
)
from core.tests.mixins import CustomAssertionsMixin
from movie_loggers.services.trakt.services import Trakt
from movies.models import Movie
from movie_loggers.services.base import MovieLogger

class TraktSystemTestCase(StaticLiveServerTestCase, CustomAssertionsMixin):
    fixtures = ["movies.json", "countries.json", "genres.json"]

    def setUp(self):
        self.movie = Movie.objects.get(pk=1)
        self.browser = webdriver.Chrome(CHROME_OPTIONS)
        self.browser.implicitly_wait(10)

    def tearDown(self):
        self.browser.quit()
        super().tearDownClass()

    def test_adding_to_watchlist_success(self):
        selenium_sign_in_user(self, MovieLogger.TRAKT.value)
        fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)
        mocked_response = {
            "body": {"not_found": {"movies": []}},
        }
        message = f"'{self.movie.title}' has been added to Trakt's watchlist."
        with stub_request(Trakt, response=mocked_response):
            self.browser.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            self.assertJsFlashMessage(message)

    def test_adding_to_watchlist_movie_not_found(self):
        selenium_sign_in_user(self, MovieLogger.TRAKT.value)
        fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)
        mocked_response = {
            "body": {"not_found": {"movies": [
                {"ids": {"imdb": self.movie.imdb_id}}
            ]}},
        }
        message = f"Trakt couldn't find '{self.movie.title}'."
        with stub_request(Trakt, response=mocked_response):
            self.browser.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            self.assertJsFlashMessage(message)

    def test_account_is_locked(self):
        selenium_sign_in_user(self, MovieLogger.TRAKT.value)
        fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)
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
            self.browser.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            self.assertJsFlashMessage(message)

    def test_account_is_deactivated(self):
        selenium_sign_in_user(self, MovieLogger.TRAKT.value)
        fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)
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
            self.browser.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            self.assertJsFlashMessage(message)

    def test_vip_account_reached_limit(self):
        selenium_sign_in_user(self, MovieLogger.TRAKT.value)
        fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)
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
            self.browser.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            self.assertJsFlashMessage(message)
