from selenium import webdriver
from selenium.webdriver.common.by import By
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from project.settings import CHROME_OPTIONS
from core.tests.mixins import CustomAssertionsMixin, CustomSeleniumMixin
from core.tests.utils import stub_requests, fill_and_submit_movie_finder_form
from movie_loggers.services.simkl.services import Simkl
from movies.models import Movie
from movie_loggers.services.base import MovieLogger


class SimklSystemTestCase(
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
        self.selenium_sign_in_user(MovieLogger.SIMKL.value)
        mocked_responses = [
            {
                "body": []
            },
            {
                "body": {"not_found": {"movies": []}},
            },
        ]
        with stub_requests(Simkl, responses=mocked_responses):
            fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)

            self.browser.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            message = f"'{self.movie.title}' has been added to Simkl's watchlist."
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
        self.selenium_sign_in_user(MovieLogger.SIMKL.value)
        mocked_responses = [
            {
                "body": []
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
        with stub_requests(Simkl, responses=mocked_responses):
            fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)

            self.browser.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            message = f"Simkl couldn't find '{self.movie.title}'."
            self.assertJsFlashMessage(message)

    def test_movie_is_marked_as_watched(self):
        self.selenium_sign_in_user(MovieLogger.SIMKL.value)
        mocked_responses = [
            {
                "body": {
                    "movies": [
                        {
                            "status": Simkl.MOVIE_STATUS_COMPLETED,
                            "movie": {
                                "ids": {
                                    "imdb": self.movie.imdb_id,
                                    "tmdb": str(self.movie.tmdb_id),
                                }
                            }
                        },
                    ]
                }
            },
        ]
        with stub_requests(Simkl, responses=mocked_responses):
            fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)
        text = "Watched"
        span = self.browser.find_element(
            By.XPATH,
            f"//div[@id='{self.movie.slug}']//span[normalize-space(text()) = '{text}']"
        )
        self.assertTrue(span)

    def test_movie_is_marked_as_on_watchlist(self):
        self.selenium_sign_in_user(MovieLogger.SIMKL.value)
        mocked_responses = [
            {
                "body": {
                    "movies": [
                        {
                            "status": Simkl.MOVIE_STATUS_PLANTOWATCH,
                            "movie": {
                                "ids": {
                                    "imdb": self.movie.imdb_id,
                                    "tmdb": str(self.movie.tmdb_id),
                                }
                            }
                        },
                    ]
                }
            }
        ]
        with stub_requests(Simkl, responses=mocked_responses):
            fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)
        text = "On watchlist"
        button = self.browser.find_element(
            By.XPATH, f"//div[@id='{self.movie.slug}']//button[normalize-space(text()) = '{text}']"
        )
        self.assertTrue(button)
        button.click()
        self.refuteJsFlashMessage()


    def test_movie_is_marked_as_watched_and_on_watchlist(self):
        self.selenium_sign_in_user(MovieLogger.SIMKL.value)
        mocked_responses = [
            {
                "body": {
                    "movies": [
                        {
                            "status": Simkl.MOVIE_STATUS_PLANTOWATCH,
                            "movie": {
                                "ids": {
                                    "imdb": self.movie.imdb_id,
                                    "tmdb": str(self.movie.tmdb_id),
                                }
                            }
                        },
                        {
                            "status": Simkl.MOVIE_STATUS_COMPLETED,
                            "movie": {
                                "ids": {
                                    "imdb": self.movie.imdb_id,
                                    "tmdb": str(self.movie.tmdb_id),
                                }
                            }
                        },
                    ]
                }
            }
        ]
        with stub_requests(Simkl, responses=mocked_responses):
            fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)
        text = "Watched"
        span = self.browser.find_element(
            By.XPATH,
            f"//div[@id='{self.movie.slug}']//span[normalize-space(text()) = '{text}']"
        )
        self.assertTrue(span)
        text = "On watchlist"
        button = self.browser.find_element(
            By.XPATH,
            f"//div[@id='{self.movie.slug}']//button[normalize-space(text()) = '{text}']"
        )
        self.assertTrue(button)
        button.click()
        self.refuteJsFlashMessage()
