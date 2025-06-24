from django.test import TestCase

from movies.models import Movie, Genre
from movies.services.movie_finder import MovieFinder
from movies.tests.utils import create_dummy_movie

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

    def test_find_movies_that_match_some_criteria(self):
        params = {
            "years": [self.default_year]
        }
        movies = MovieFinder(**params).perform()
        self.assertEqual(len(movies), Movie.objects.count())

        self.movie_without_genres.year = self.default_year - 1
        self.movie_without_genres.save()
        self.movie_fantasy.year = self.default_year - 1
        self.movie_fantasy.save()
        params = {
            "genres": ["Drama"],
            "years": [self.default_year]
        }
        movies = MovieFinder(**params).perform()
        self.assertNotIn(self.movie_without_genres, movies)
        self.assertNotIn(self.movie_fantasy, movies)

    def test_find_movies_that_match_all_criteria(self):
        params = {
            "match_some_criteria": False,
            "genres": ["Drama", "Reality"]
        }
        movies = MovieFinder(**params).perform()
        self.assertEqual(len(movies), 1)
        self.assertEqual(movies[0], self.movie_drama_reality)
