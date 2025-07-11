from http import HTTPStatus

from selenium import webdriver
from selenium.webdriver.common.by import By
from requests.exceptions import HTTPError
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from project.settings import CHROME_OPTIONS
from core.tests.utils import (
    stub_requests,
    mock_response,
    fill_and_submit_movie_finder_form,
)
from core.tests.mixins import CustomAssertionsMixin, CustomSeleniumMixin
from core.enums import MovieStatus
from movie_loggers.services.tmdb.services import TMDB
from movies.models import Movie
from movie_loggers.services.base import MovieLogger

class TMDBSystemTestCase(
    StaticLiveServerTestCase,
    CustomAssertionsMixin,
    CustomSeleniumMixin,
):
    fixtures = ["movies.json", "countries.json", "genres.json"]

    def setUp(self):
        self.movie = Movie.objects.get(pk=1)
        self.browser = webdriver.Chrome(CHROME_OPTIONS)
        self.browser.implicitly_wait(1)

    def tearDown(self):
        self.browser.quit()
        super().tearDownClass()

    def test_adding_to_watchlist_success(self):
        self.selenium_sign_in_user(MovieLogger.TMDB.value)

        mocked_responses = [
            {
                "body": {
                    "results": [],
                    "total_pages": 1,
                },
            },
            {
                "body": {"success": True},
            },
        ]
        with stub_requests(TMDB, responses=mocked_responses):
            fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)

            self.browser.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            message = f"'{self.movie.title}' has been added to TMDB's watchlist."
            self.assertJsFlashMessage(message)
        self.browser.refresh()
        text = "Added to watchlist"
        button = self.browser.find_element(
            By.XPATH,
            f"//div[@id='{self.movie.slug}']//button[normalize-space(text()) = '{text}']"
        )
        button.click()
        self.refuteJsFlashMessage()

    def test_adding_to_watchlist_fail(self):
        self.selenium_sign_in_user(MovieLogger.TMDB.value)
        mocked_exception_response = {
            "body": {},
            "status_code": HTTPStatus.BAD_REQUEST.value,
        }
        exception = HTTPError(
            HTTPStatus.BAD_REQUEST.phrase,
            response=mock_response(mocked_exception_response)
        )
        mocked_responses = [
            {
                "body": {
                    "results": [],
                    "total_pages": 1,
                },
            },
            exception,
        ]
        with stub_requests(TMDB, responses=mocked_responses):
            fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)

            self.browser.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            message = f"Something went wrong while trying to add {self.movie.title} to your TMDB's watchlist."
            self.assertJsFlashMessage(message)

    def test_movie_is_marked_as_on_watchlist(self):
        self.selenium_sign_in_user(MovieLogger.TMDB.value)
        total_pages = 1
        mocked_responses = [
            {
                "body": {
                    "results": [
                        {
                            "id": self.movie.tmdb_id,
                        },
                    ],
                    "total_pages": 1,
                }
            },
        ]
        with stub_requests(TMDB, responses=mocked_responses):
            fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)
        text = MovieStatus.ON_WATCHLIST.value
        button = self.browser.find_element(
            By.XPATH, f"//div[@id='{self.movie.slug}']//button[normalize-space(text()) = '{text}']"
        )
        self.assertTrue(button)
        button.click()
        self.refuteJsFlashMessage()
