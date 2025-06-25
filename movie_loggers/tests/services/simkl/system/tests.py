from selenium import webdriver
from selenium.webdriver.common.by import By
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

# TODO: Rename them to plural form for consistency e.g. 'tests' instead of 'test'
from project.settings import CHROME_OPTIONS
from core.tests.utils import stub_request
from core.tests.mixins import CustomAssertionsMixin
from oauth.tests.utils import selenium_sign_in_user
from movie_loggers.services.simkl import Simkl
from movies.models import Movie
from movie_loggers.services.base import MovieLogger
from movies.tests.utils import create_dummy_movie


class SimklSystemTestCase(StaticLiveServerTestCase, CustomAssertionsMixin):
    fixtures = ["movies.json", "countries.json"]

    def setUp(self):
        self.movie = Movie.objects.get(pk=1)
        # For a good measure create 4 more
        for _ in range(4):
            create_dummy_movie(self.movie)
        self.selenium = webdriver.Chrome(CHROME_OPTIONS)
        self.selenium.implicitly_wait(10)

    def tearDown(self):
        self.selenium.quit()
        super().tearDownClass()

    def test_adding_to_watchlist_success(self):
        selenium_sign_in_user(self, MovieLogger.SIMKL.value)
        url = reverse("movies:index")
        self.selenium.get(f"{self.live_server_url}/{url}")
        mocked_response = {
            "body": {"not_found": {"movies": []}},
        }
        message = f"'{self.movie.title}' has been added to Simkl's watchlist."
        with stub_request(Simkl, response=mocked_response):
            self.selenium.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            self.assertJsFlashMessage(message)


    def test_adding_to_watchlist_movie_not_found(self):
        selenium_sign_in_user(self, MovieLogger.SIMKL.value)
        url = reverse("movies:index")
        self.selenium.get(f"{self.live_server_url}/{url}")
        mocked_response = {
            "body": {"not_found": {"movies": [
                {"ids": {"imdb": self.movie.imdb_id}}
            ]}},
        }
        message = f"Simkl couldn't find '{self.movie.title}'."
        with stub_request(Simkl, response=mocked_response):
            self.selenium.find_element(
                By.XPATH, f"//button[@id='add-to-watchlist-{self.movie.tvdb_id}']"
            ).click()
            self.assertJsFlashMessage(message)
