from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from movies.models import Movie
from movie_metadata.services import MovieMetadata
from core.tests.utils import stub_requests
from core.files.utils import read_json_file

class AddNewMoviesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fetch_latest_movie_id_patcher = patch('movie_metadata.services.MovieMetadata.TMDB._fetch_latest_movie_id', return_value=2)
        cls.mock_fetch_latest_movie_id = cls.fetch_latest_movie_id_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.fetch_latest_movie_id_patcher.stop()

    def setUp(self):
        self.movies_dir = Path("movies/samples")

        self.movie_1_file = Path(self.movies_dir / "frozen_stiff.json")
        self.movie_2_file = Path(self.movies_dir / "gladiator.json")
        self.movie_1_file_content = read_json_file(self.movie_1_file)
        self.movie_2_file_content = read_json_file(self.movie_2_file)

        self.tmdb = MovieMetadata.TMDB()

    def test_add_new_movies(self):
        responses = [
            {"body": self.movie_1_file_content},
            {"body": self.movie_2_file_content},
        ]
        self.assertEqual(Movie.objects.count(), 0)

        with stub_requests(self.tmdb, responses=responses):
            call_command("add_new_movies")
        self.assertEqual(Movie.objects.count(), 2)
