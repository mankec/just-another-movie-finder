from selenium import webdriver
from selenium.webdriver.common.by import By
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from project.settings import CHROME_OPTIONS
from core.tests.mixins import CustomAssertionsMixin
from core.tests.utils import (
    stub_request,
    selenium_sign_in_user,
    fill_and_submit_movie_finder_form,
)
from movie_loggers.services.simkl.services import Simkl
from movies.models import Movie
from movie_loggers.services.base import MovieLogger


class SimklSystemTestCase(StaticLiveServerTestCase, CustomAssertionsMixin):
    fixtures = ["movies.json", "countries.json", "genres.json"]

    def setUp(self):
        self.movie = Movie.objects.get(pk=1)

        self.browser = webdriver.Chrome(CHROME_OPTIONS)
        self.browser.implicitly_wait(10)

    def tearDown(self):
        self.browser.quit()
        super().tearDownClass()

    def test_adding_to_watchlist_success(self):
        selenium_sign_in_user(self, MovieLogger.SIMKL.value)
        fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)
        mocked_response = {
            "body": {"not_found": {"movies": []}},
        }
        message = f"'{self.movie.title}' has been added to Simkl's watchlist."
        with stub_request(Simkl, response=mocked_response):
            self.browser.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            self.assertJsFlashMessage(message)

    def test_adding_to_watchlist_movie_not_found(self):
        selenium_sign_in_user(self, MovieLogger.SIMKL.value)
        fill_and_submit_movie_finder_form(self.browser, year_from=self.movie.year)
        mocked_response = {
            "body": {"not_found": {"movies": [
                {"ids": {"imdb": self.movie.imdb_id}}
            ]}},
        }
        message = f"Simkl couldn't find '{self.movie.title}'."
        with stub_request(Simkl, response=mocked_response):
            self.browser.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            self.assertJsFlashMessage(message)
