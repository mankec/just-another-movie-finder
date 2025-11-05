from django.test import TestCase

from core.tests.utils import create_dummy_movie
from core.constants import DEFAULT_YEAR
from movies.languages.constants import DEFAULT_LANGUAGE_ISO_639_1
from movies.countries.constants import DEFAULT_COUNTRY_ISO_3166_1
from movies.models import Movie, Genre
from movies.services.movie_finder.services import MovieFinder

class MovieFinderUnitTestCase(TestCase):
    fixtures = ["movies.json", "genres.json"]

    def setUp(self):
        self.genre_drama = Genre.objects.get(name="Drama")
        self.genre_comedy = Genre.objects.get(name="Comedy")
        self.genre_fantasy = Genre.objects.get(name="Fantasy")
        self.genre_action = Genre.objects.get(name="Action")
        self.runtime = 90

        self.serbian_movie_drama_comedy = Movie.objects.get(pk=1)
        self.serbian_movie_drama_comedy.runtime = self.runtime
        self.serbian_movie_drama_comedy.genres.add(self.genre_drama, self.genre_comedy)
        self.serbian_movie_drama_comedy.save()

        self.irish_movie_drama_fantasy = create_dummy_movie()
        self.irish_movie_drama_fantasy.origin_country = ["Ireland"]
        self.irish_movie_drama_fantasy.year = DEFAULT_YEAR
        self.irish_movie_drama_fantasy.runtime = self.runtime + 10
        self.irish_movie_drama_fantasy.genres.add(self.genre_drama, self.genre_fantasy)
        self.irish_movie_drama_fantasy.save()

        self.exclude_movie = create_dummy_movie()
        self.exclude_movie.origin_country = ["Spain"]
        self.exclude_movie.genres.add(self.genre_action)
        self.exclude_movie.save()

        self.params = {
            "country": "",
            "language": "",
            "genres": [],
            "exclude_genres": [],
            "year_from": "",
            "year_to": "",
            "runtime_min": "",
            "runtime_max": "",
        }

    def test_find_movies_without_excluding_genres(self):
        self.params["country"] = DEFAULT_COUNTRY_ISO_3166_1
        self.params["language"] = DEFAULT_LANGUAGE_ISO_639_1
        self.params["genres"] = [self.genre_drama.id, self.genre_comedy.id]

        movie_ids = MovieFinder(**self.params).get_movie_ids()
        self.assertIn(self.serbian_movie_drama_comedy.id, movie_ids)
        self.assertNotIn(self.irish_movie_drama_fantasy.id, movie_ids)
        self.assertNotIn(self.exclude_movie.id, movie_ids)

    def test_find_movies_with_excluding_genres(self):
        self.params["genres"] = [self.genre_drama.id]
        self.params["exclude_genres"] = [self.genre_fantasy.id, self.genre_action.id]
        movie_ids = MovieFinder(**self.params).get_movie_ids()
        self.assertIn(self.serbian_movie_drama_comedy.id, movie_ids)
        self.assertNotIn(self.irish_movie_drama_fantasy.id, movie_ids)
        self.assertNotIn(self.exclude_movie.id, movie_ids)

        self.params["genres"] = [self.genre_drama.id]
        self.params["exclude_genres"] = [self.genre_action.id]
        movie_ids = MovieFinder(**self.params).get_movie_ids()
        self.assertIn(self.serbian_movie_drama_comedy.id, movie_ids)
        self.assertIn(self.irish_movie_drama_fantasy.id, movie_ids)
        self.assertNotIn(self.exclude_movie.id, movie_ids)

    def test_find_movies_only_year_from_is_present(self):
        self.exclude_movie.year = DEFAULT_YEAR - 10
        self.exclude_movie.save()
        self.params["year_from"] = DEFAULT_YEAR

        movie_ids = MovieFinder(**self.params).get_movie_ids()
        self.assertIn(self.serbian_movie_drama_comedy.id, movie_ids)
        self.assertIn(self.irish_movie_drama_fantasy.id, movie_ids)
        self.assertNotIn(self.exclude_movie.id, movie_ids)

    def test_find_movies_year_range(self):
        self.exclude_movie.year = DEFAULT_YEAR + 10
        self.exclude_movie.save()
        self.params["year_from"] = DEFAULT_YEAR
        self.params["year_to"] = DEFAULT_YEAR + 5

        movie_ids = MovieFinder(**self.params).get_movie_ids()
        self.assertIn(self.serbian_movie_drama_comedy.id, movie_ids)
        self.assertIn(self.irish_movie_drama_fantasy.id, movie_ids)
        self.assertNotIn(self.exclude_movie.id, movie_ids)

    def test_find_movies_only_year_to_is_present(self):
        self.exclude_movie.year = DEFAULT_YEAR + 10
        self.exclude_movie.save()
        self.params["year_to"] = DEFAULT_YEAR

        movie_ids = MovieFinder(**self.params).get_movie_ids()
        self.assertIn(self.serbian_movie_drama_comedy.id, movie_ids)
        self.assertIn(self.irish_movie_drama_fantasy.id, movie_ids)
        self.assertNotIn(self.exclude_movie.id, movie_ids)

    def test_find_movies_only_runtime_min_is_present(self):
        self.exclude_movie.runtime = self.runtime - 10
        self.exclude_movie.save()
        self.params["runtime_min"] = self.runtime

        movie_ids = MovieFinder(**self.params).get_movie_ids()
        self.assertIn(self.serbian_movie_drama_comedy.id, movie_ids)
        self.assertIn(self.irish_movie_drama_fantasy.id, movie_ids)
        self.assertNotIn(self.exclude_movie.id, movie_ids)

    def test_find_movies_runtime_range(self):
        self.exclude_movie.runtime = self.runtime - 10
        self.exclude_movie.save()
        self.params["runtime_min"] = self.runtime
        self.params["runtime_max"] = self.runtime + 30

        movie_ids = MovieFinder(**self.params).get_movie_ids()
        self.assertIn(self.serbian_movie_drama_comedy.id, movie_ids)
        self.assertIn(self.irish_movie_drama_fantasy.id, movie_ids)
        self.assertNotIn(self.exclude_movie.id, movie_ids)

    def test_find_movies_only_runtime_max_is_present(self):
        self.exclude_movie.runtime = self.runtime + 10
        self.exclude_movie.save()
        self.params["runtime_max"] = self.runtime

        movie_ids = MovieFinder(**self.params).get_movie_ids()
        self.assertIn(self.serbian_movie_drama_comedy.id, movie_ids)
        self.assertNotIn(self.irish_movie_drama_fantasy.id, movie_ids)
        self.assertNotIn(self.exclude_movie.id, movie_ids)
