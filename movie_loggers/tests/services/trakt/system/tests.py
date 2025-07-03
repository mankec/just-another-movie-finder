from http import HTTPStatus

from selenium import webdriver
from selenium.webdriver.common.by import By
from requests.exceptions import HTTPError
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from project.settings import CHROME_OPTIONS
from core.tests.utils import (
    stub_requests,
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
        self.browser.implicitly_wait(1)

    def tearDown(self):
        self.browser.quit()
        super().tearDownClass()

    def test_adding_to_watchlist_success(self):
        selenium_sign_in_user(self, MovieLogger.TRAKT.value)
        mocked_responses = [
            {
                "body": [],
            },
            {
                "body": [],
                "headers": {
                    "X-Pagination-Page-Count": 0,
                }
            },
        ]
        with stub_requests(Trakt, responses=mocked_responses):
            fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)

        mocked_response = [
            {
                "body": {"not_found": {"movies": []}},
            },
        ]
        with stub_requests(Trakt, responses=mocked_response):
            self.browser.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            message = f"'{self.movie.title}' has been added to Trakt's watchlist."
            self.assertJsFlashMessage(message)
        self.browser.refresh()
        text = "Added to watchlist"
        button = self.browser.find_element(
            By.XPATH,
            f"//div[@id='{self.movie.slug}']//button[normalize-space(text()) = '{text}']"
        )
        button.click()
        self.refuteJsFlashMessage()

    def test_adding_to_watchlist_movie_not_found(self):
        selenium_sign_in_user(self, MovieLogger.TRAKT.value)
        mocked_responses = [
            {
                "body": [],
            },
            {
                "body": [],
                "headers": {
                    "X-Pagination-Page-Count": 0,
                }
            },
            {
                "body": {
                    "not_found": {
                        "movies": [
                            {
                                "ids": {
                                    "imdb": self.movie.imdb_id
                                }
                            }
                        ]
                    }
                },
            },
        ]
        with stub_requests(Trakt, responses=mocked_responses):
            fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)

            self.browser.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            message = f"Trakt couldn't find '{self.movie.title}'."
            self.assertJsFlashMessage(message)

    def test_account_is_locked(self):
        selenium_sign_in_user(self, MovieLogger.TRAKT.value)
        mocked_exception_response = {
            "body": {},
            "status_code": HTTPStatus.LOCKED.value,
            "headers": {
                "X-Account-Locked": "true",
                "X-Account-Deactivated": "false",
            },
        }
        exception = HTTPError(
            HTTPStatus.LOCKED.phrase,
            response=mock_response(mocked_exception_response)
        )
        mocked_responses = [
            {
                "body": [],
            },
            {
                "body": [],
                "headers": {
                    "X-Pagination-Page-Count": 0,
                }
            },
            exception,
        ]
        with stub_requests(Trakt, responses=mocked_responses):
            fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)

            self.browser.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            message = "Your Trakt account is locked. Please contact their support at support@trakt.tv."
            self.assertJsFlashMessage(message)

    def test_account_is_deactivated(self):
        selenium_sign_in_user(self, MovieLogger.TRAKT.value)
        mocked_exception_response = {
            "body": {},
            "status_code": HTTPStatus.LOCKED.value,
            "headers": {
                "X-Account-Locked": "false",
                "X-Account-Deactivated": "true",
            }
        }
        exception = HTTPError(
            HTTPStatus.LOCKED.phrase,
            response=mock_response(mocked_exception_response)
        )
        mocked_responses = [
            {
                "body": [],
            },
            {
                "body": [],
                "headers": {
                    "X-Pagination-Page-Count": 0,
                }
            },
            exception,
        ]
        with stub_requests(Trakt, responses=mocked_responses):
            fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)

            self.browser.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            message = "Your Trakt account is deactivated. Please contact their support at support@trakt.tv."
            self.assertJsFlashMessage(message)

    def test_vip_account_reached_limit(self):
        selenium_sign_in_user(self, MovieLogger.TRAKT.value)
        mocked_exception_response = {
            "body": {},
            "status_code": Trakt.HTTP_STATUS_CODE_VIP_ENHANCED,
            "headers": {
                "X-Upgrade-URL": Trakt.VIP_UPGRADE_URL,
                "X-VIP-User": "true",
            }
        }
        exception = HTTPError(response=mock_response(mocked_exception_response))
        mocked_responses = [
            {
                "body": [],
            },
            {
                "body": [],
                "headers": {
                    "X-Pagination-Page-Count": 0,
                }
            },
            exception,
        ]
        with stub_requests(Trakt, responses=mocked_responses):
            fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)

            self.browser.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            message = "You have reached limit for your Trakt account."
            self.assertJsFlashMessage(message)

    def test_movie_is_marked_as_watched(self):
        selenium_sign_in_user(self, MovieLogger.TRAKT.value)
        total_pages = 1
        mocked_responses = [
            {
                "body": [
                    {
                        "movie": {
                            "ids": {
                                "imdb": self.movie.imdb_id,
                                "tmdb": str(self.movie.tmdb_id),
                            }
                        }
                    }
                ],
            },
            {
                "body": [],
                "headers": { "X-Pagination-Page-Count": total_pages },
            },
        ]
        with stub_requests(Trakt, responses=mocked_responses):
            fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)
        text = "Watched"
        span = self.browser.find_element(
            By.XPATH,
            f"//div[@id='{self.movie.slug}']//span[normalize-space(text()) = '{text}']"
        )
        self.assertTrue(span)


    def test_movie_is_marked_as_on_watchlist(self):
        selenium_sign_in_user(self, MovieLogger.TRAKT.value)
        total_pages = 1
        mocked_responses = [
            {
                "body": [],
            },
            {
                "body": [
                    {
                        "movie": {
                            "ids": {
                                "imdb": self.movie.imdb_id,
                                "tmdb": str(self.movie.tmdb_id),
                            }
                        }
                    }
                ],
                "headers": { "X-Pagination-Page-Count": total_pages },
            },
        ]
        with stub_requests(Trakt, responses=mocked_responses):
            fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)
        text = "On watchlist"
        button = self.browser.find_element(
            By.XPATH, f"//div[@id='{self.movie.slug}']//button[normalize-space(text()) = '{text}']"
        )
        self.assertTrue(button)
        button.click()
        self.refuteJsFlashMessage()

    def test_movie_is_marked_as_watched_and_on_watchlist(self):
        selenium_sign_in_user(self, MovieLogger.TRAKT.value)
        total_pages = 1
        mocked_responses = [
            {
                "body": [
                    {
                        "movie": {
                            "ids": {
                                "imdb": self.movie.imdb_id,
                                "tmdb": str(self.movie.tmdb_id),
                            }
                        }
                    }
                ],
            },
            {
                "body": [
                    {
                        "movie": {
                            "ids": {
                                "imdb": self.movie.imdb_id,
                                "tmdb": str(self.movie.tmdb_id),
                            }
                        }
                    }
                ],
                "headers": { "X-Pagination-Page-Count": total_pages },
            },
        ]
        with stub_requests(Trakt, responses=mocked_responses):
            fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)

        text = "Watched"
        span = self.browser.find_element(
            By.XPATH,
            f"//div[@id='{self.movie.slug}']//span[normalize-space(text()) = '{text}']"
        )
        self.assertTrue(span)
        # TODO: Put this into enum e.g. MovieStatus
        text = "On watchlist"
        button = self.browser.find_element(
            By.XPATH, f"//div[@id='{self.movie.slug}']//button[normalize-space(text()) = '{text}']"
        )
        self.assertTrue(button)
        button.click()
        self.refuteJsFlashMessage()
