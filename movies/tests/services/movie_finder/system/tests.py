from selenium import webdriver
from selenium.webdriver.common.by import By
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from project.settings import CHROME_OPTIONS
from core.tests.mixins import CustomAssertionsMixin
from core.tests.utils import fill_and_submit_movie_finder_form
from core.constants import DEFAULT_COUNTRY, DEFAULT_LANGUAGE, DEFAULT_YEAR
from movies.models import Movie, Country, Genre
from core.tests.utils import create_dummy_movie

class MovieFinderSystemTestCase(StaticLiveServerTestCase, CustomAssertionsMixin):
    fixtures = ["movies.json", "countries.json", "genres.json"]

    def test_each_form_field_and_search_work_properly(self):
        self.browser = webdriver.Chrome(CHROME_OPTIONS)
        include_countries = [DEFAULT_COUNTRY, "Ireland"]
        exclude_countries = ["Spain", "France"]
        include_languages = [DEFAULT_LANGUAGE, "Irish"]
        exclude_languages = ["Spanish", "French"]
        include_genres = ["Reality", "Drama"]
        exclude_genres = ["Action", "Fantasy"]

        movie = Movie.objects.get(pk=1)
        movie.country = Country.objects.get(name=DEFAULT_COUNTRY)
        movie.language = exclude_languages[0]
        movie.genres.add(
            Genre.objects.get(name=include_genres[0]),
            Genre.objects.get(name=include_genres[1]),
        )
        movie.save()
        exclude_movie = create_dummy_movie(movie)
        exclude_movie.country = Country.objects.get(name=exclude_countries[0])
        exclude_movie.language = exclude_languages[0]
        exclude_movie.genres.add(
            Genre.objects.get(name=exclude_genres[0]),
            Genre.objects.get(name=exclude_genres[1]),
        )
        exclude_movie.save()

        self.browser.get(self.live_server_url)
        fill_and_submit_movie_finder_form(
            self.browser,
            countries=include_countries,
            exclude_countries=exclude_countries,
            languages=include_languages,
            exclude_languages=exclude_languages,
            genres=include_genres,
            exclude_genres=exclude_genres,
            year_from=DEFAULT_YEAR,
            year_to=DEFAULT_YEAR,
            runtime_min=90,
            runtime_max=120,
        )
        self.browser.find_element(By.ID, movie.slug)
        self.assertFalse(self.browser.find_elements(By.ID, exclude_movie.slug))
        text = "Add to watchlist"
        title = "You must be signed in to be able to add movies to watchlist"
        button = self.browser.find_element(
            By.XPATH,
            f"//div[@id='{movie.slug}']//button[@title='{title}' and normalize-space(text()) = '{text}']"
        )
        button.click()
        self.refuteJsFlashMessage()

        self.browser.quit()
