from django.test import TestCase

from movies.models import Movie, Genre
from movies.services.movie_finder.services import MovieFinder
from core.tests.utils import create_dummy_movie
from movies.forms.movie_finder.forms import MATCH_FILTERS_SOME, MATCH_FILTERS_ALL

class MovieFinderUnitTestCase(TestCase):
    fixtures = ["movies.json", "genres.json", "countries.json"]

    def setUp(self):
        self.genre_drama = Genre.objects.get(name="Drama")
        self.genre_reality = Genre.objects.get(name="Reality")
        self.genre_fantasy = Genre.objects.get(name="Fantasy")

        self.movie_without_genres = Movie.objects.get(pk=1)
        self.movie_drama = create_dummy_movie(self.movie_without_genres)
        self.movie_fantasy = create_dummy_movie(self.movie_without_genres)
        self.movie_drama_reality = create_dummy_movie(self.movie_without_genres)
        self.movie_drama_fantasy = create_dummy_movie(self.movie_drama)

        self.movie_drama.genres.add(self.genre_drama)
        self.movie_drama.save()
        self.movie_fantasy.genres.add(self.genre_fantasy)
        self.movie_fantasy.save()
        self.movie_drama_reality.genres.add(self.genre_drama, self.genre_reality)
        self.movie_drama_reality.save()
        self.movie_drama_fantasy.genres.add(self.genre_drama, self.genre_fantasy)
        self.movie_drama_fantasy.save()

        self.default_year = self.movie_without_genres.year

        self.params = {
            "countries": [],
            "languages": [],
            "genres": [],
            "exclude_countries": [],
            "exclude_languages": [],
            "exclude_genres": [],
            "year_from": "",
            "year_to": "",
            "runtime_min": "",
            "runtime_max": "",
            "match_filters": MATCH_FILTERS_SOME,
        }

    #TODO: Write test that covers all fields in both 'some' and 'all' cases.
    def test_find_movies_that_match_some_filters(self):
        self.params["year_from"] = self.default_year
        self.params["year_to"] = self.default_year
        movies = MovieFinder(**self.params).get_movie_ids()
        self.assertTrue(movies)
        self.assertEqual(len(movies), Movie.objects.count())

        self.movie_without_genres.year = self.default_year - 1
        self.movie_without_genres.save()
        self.movie_fantasy.year = self.default_year - 1
        self.movie_fantasy.save()
        self.params["genres"] = [self.genre_drama.slug]
        movie_ids = MovieFinder(**self.params).get_movie_ids()
        self.assertIn(self.movie_drama.tvdb_id, movie_ids)
        self.assertIn(self.movie_drama_reality.tvdb_id, movie_ids)
        self.assertIn(self.movie_drama_fantasy.tvdb_id, movie_ids)
        self.assertNotIn(self.movie_without_genres.tvdb_id, movie_ids)
        self.assertNotIn(self.movie_fantasy.tvdb_id, movie_ids)

    def test_find_movies_that_match_some_filters_with_excluding_filters(self):
        self.params["year_from"] = self.default_year
        self.params["year_to"] = self.default_year
        movie_ids = MovieFinder(**self.params).get_movie_ids()
        self.assertEqual(len(movie_ids), Movie.objects.count())

        self.movie_fantasy.save()
        self.params["genres"] = [self.genre_drama.slug]
        self.params["exclude_genres"] = [self.genre_reality.slug, self.genre_fantasy.slug]
        movie_ids = MovieFinder(**self.params).get_movie_ids()
        self.assertIn(self.movie_drama.tvdb_id, movie_ids)
        self.assertIn(self.movie_without_genres.tvdb_id, movie_ids)
        self.assertNotIn(self.movie_fantasy.tvdb_id, movie_ids)
        self.assertNotIn(self.movie_drama_fantasy.tvdb_id, movie_ids)
        self.assertNotIn(self.movie_drama_reality.tvdb_id, movie_ids)

    def test_find_movies_that_match_all_filters(self):
        self.params["match_filters"] = MATCH_FILTERS_ALL
        self.params["genres"] = [self.genre_drama.slug, self.genre_reality.slug]
        movie_ids = MovieFinder(**self.params).get_movie_ids()
        self.assertEqual(len(movie_ids), 1)
        self.assertEqual(movie_ids[0], self.movie_drama_reality.tvdb_id)
