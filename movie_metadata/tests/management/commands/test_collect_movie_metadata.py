import tempfile
from pathlib import Path
from unittest.mock import patch
from http import HTTPStatus

from django.core.management import call_command
from django.test import TestCase

from movie_metadata.services.base import MovieMetadata
# TODO: Move this to project utils
from movie_loggers.tests.services.helpers import stub_request, stub_multiple_requests
from project.utils import read_file, create_empty_json_file, write_to_json_file

class CollectMovieMetadataTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fetch_token_patcher = patch('movie_metadata.services.base.MovieMetadata.TVDB._fetch_token', return_value="token")
        cls.mock_fetch_token = cls.fetch_token_patcher.start()

        cls.fetch_total_movies_patcher = patch('movie_metadata.services.base.MovieMetadata.TVDB._fetch_total_movies', return_value=2)
        cls.mock_fetch_total_movies = cls.fetch_total_movies_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.fetch_token_patcher.stop()
        cls.fetch_total_movies_patcher.stop()

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_metadata_dir = Path(self.tmp_dir.name) / "movie_metadata" / "metadata"
        self.tmp_backup_dir = Path(self.tmp_dir.name) / "movie_metadata" / "backup"
        self.metadata_file_name = "metadata_0001.json"
        self.metadata_file_name_2 = "metadata_0002.json"
        self.movies_dir = Path("movie_metadata/filesamples/movies")

        movie_1_file = Path(self.movies_dir / "frozen_stiff.json")
        movie_2_file = Path(self.movies_dir / "gladiator.json")
        self.movie_1_file_content = read_file(movie_1_file)
        self.movie_2_file_content = read_file(movie_2_file)

        self.tvdb = MovieMetadata.TVDB()

        self.tmp_metadata_dir.mkdir(parents=True)
        self.tmp_backup_dir.mkdir(parents=True)

        self.backup_file = create_empty_json_file(self.tmp_backup_dir / self.metadata_file_name, json_type="arr")
        self.metadata_file = create_empty_json_file(self.tmp_metadata_dir / self.metadata_file_name, json_type="arr")
        self.not_found_movie_ids_file = create_empty_json_file(Path(self.tmp_dir.name) / "movie_metadata" / "not_found_movie_ids.json", json_type="arr")

    def _collect_movie_metadata(self, max_movies_per_file=2):
        call_command(
            "collect_movie_metadata",
            metadata_dir_path=self.tmp_metadata_dir,
            backup_dir_path=self.tmp_backup_dir,
            not_found_movie_ids_file_path = self.not_found_movie_ids_file,
            max_movies_per_file=max_movies_per_file
        )

    def test_initial_call(self):
        self.backup_file.unlink()
        self.metadata_file.unlink()
        responses = [
            {"body": self.movie_1_file_content},
            {"body": self.movie_2_file_content},
        ]
        expected = [
            self.movie_1_file_content["data"],
            self.movie_2_file_content["data"],
        ]
        with stub_multiple_requests(self.tvdb, responses=responses):
            self._collect_movie_metadata()
        data = read_file(self.metadata_file)
        self.assertEqual(data, expected)

    def test_with_valid_data(self):
        responses = [
            {"body": self.movie_1_file_content},
            {"body": self.movie_2_file_content},
        ]
        expected = [
            self.movie_1_file_content["data"],
            self.movie_2_file_content["data"],
        ]
        with stub_multiple_requests(self.tvdb, responses=responses):
            self._collect_movie_metadata()
        data = read_file(self.metadata_file)
        self.assertEqual(data, expected)

    def test_with_corrupted_data_in_metadata_directory(self):
        backup_data = [
            self.movie_1_file_content["data"]
        ]
        write_to_json_file(backup_data, self.backup_file)

        response = {"body": self.movie_2_file_content}
        expected = [
            self.movie_1_file_content["data"],
            self.movie_2_file_content["data"],
        ]
        with patch(
            "movie_metadata.management.commands.collect_movie_metadata.Command._is_file_corrupted",
            return_value=True
        ):
            with stub_request(self.tvdb, response=response):
                self._collect_movie_metadata()
        data = read_file(self.metadata_file)
        self.assertEqual(data, expected)

    def test_movie_not_found(self):
        # Movie ID counting starts from 1 therefore movie with id 2 will raise not found exception.
        not_found_movie_id = 2
        responses = [
            {"body": self.movie_1_file_content},
            {"body": HTTPStatus.NOT_FOUND.phrase, "status_code": HTTPStatus.NOT_FOUND.value},
            {"body": self.movie_2_file_content},
        ]
        expected = [
            self.movie_1_file_content["data"],
            self.movie_2_file_content["data"],
        ]
        with stub_multiple_requests(self.tvdb, responses=responses):
            self._collect_movie_metadata()
        data = read_file(self.metadata_file)
        not_found_movie_ids = read_file(self.not_found_movie_ids_file)
        self.assertEqual(data, expected)
        self.assertEqual(not_found_movie_ids, [not_found_movie_id])
