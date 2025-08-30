import tempfile
from pathlib import Path
from unittest.mock import patch
from http import HTTPStatus

from django.core.management import call_command
from django.test import TestCase
from requests.exceptions import HTTPError

from movie_metadata.services import MovieMetadata
from core.tests.utils import stub_requests, mock_response
from core.files.utils import (
    read_json_file,
    read_jsonl_file,
    create_empty_json_file,
    create_empty_file,
    write_to_json_file,
    dir_size,
)

class CollectMovieMetadataTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fetch_latest_movie_id_patcher = patch('movie_metadata.services.MovieMetadata.TMDB._fetch_latest_movie_id', return_value=2)
        cls.mock_fetch_latest_movie_id = cls.fetch_latest_movie_id_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.fetch_latest_movie_id_patcher.stop()

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_metadata_dir = Path(self.tmp_dir.name) / "movie_metadata" / "metadata"
        self.tmp_backup_dir = Path(self.tmp_dir.name) / "movie_metadata" / "backup"
        self.metadata_file_name = "metadata_0001.jsonl"
        self.metadata_file_name_2 = "metadata_0002.jsonl"
        self.movies_dir = Path("movies/samples")

        self.movie_1_file = Path(self.movies_dir / "frozen_stiff.json")
        self.movie_2_file = Path(self.movies_dir / "gladiator.json")
        self.movie_1_file_content = read_json_file(self.movie_1_file)
        self.movie_2_file_content = read_json_file(self.movie_2_file)

        self.tmdb = MovieMetadata.TMDB()

        self.tmp_metadata_dir.mkdir(parents=True)
        self.tmp_backup_dir.mkdir(parents=True)

        self.backup_file = create_empty_file(self.tmp_backup_dir / self.metadata_file_name)
        self.metadata_file = create_empty_file(
            self.tmp_metadata_dir / self.metadata_file_name
        )
        self.not_found_movie_ids_file = create_empty_json_file(Path(self.tmp_dir.name) / "movie_metadata" / "not_found_movie_ids.json", json_type="arr")

    def tearDown(self):
        self.__class__.mock_fetch_latest_movie_id.return_value = 2

    def _collect_movie_metadata(self, max_movies_per_file=2, max_movies_per_bundled_file=1):
        call_command(
            "collect_movie_metadata",
            metadata_dir=self.tmp_metadata_dir,
            backup_dir=self.tmp_backup_dir,
            not_found_movie_ids_file = self.not_found_movie_ids_file,
            max_movies_per_file=max_movies_per_file,
            max_movies_per_bundled_file=max_movies_per_bundled_file,
        )

    def test_initial_call(self):
        self.backup_file.unlink()
        self.metadata_file.unlink()
        responses = [
            {"body": self.movie_1_file_content},
            {"body": self.movie_2_file_content},
        ]
        expected = [
            self.movie_1_file_content,
            self.movie_2_file_content,
        ]
        with stub_requests(self.tmdb, responses=responses):
            self._collect_movie_metadata()
        data = read_jsonl_file(self.metadata_file)
        self.assertEqual(data, expected)

    def test_with_valid_data(self):
        responses = [
            {"body": self.movie_1_file_content},
            {"body": self.movie_2_file_content},
        ]
        expected = [
            self.movie_1_file_content,
            self.movie_2_file_content,
        ]
        with stub_requests(self.tmdb, responses=responses):
            self._collect_movie_metadata()
        data = read_jsonl_file(self.metadata_file)
        self.assertEqual(data, expected)

    def test_movie_not_found(self):
        # Movie ID counting starts from 1 therefore movie with id 2 will raise not found exception.
        self.__class__.mock_fetch_latest_movie_id.return_value = 3
        not_found_movie_id = 2
        mocked_response = {
            "body": {},
            "status_code": HTTPStatus.NOT_FOUND.value,
        }
        responses = [
            {"body": self.movie_1_file_content},
            HTTPError(HTTPStatus.NOT_FOUND.phrase, response=mock_response(mocked_response)),
            {"body": self.movie_2_file_content},
        ]
        expected = [
            self.movie_1_file_content,
            self.movie_2_file_content,
        ]
        with stub_requests(self.tmdb, responses=responses):
            self._collect_movie_metadata()
        data = read_jsonl_file(self.metadata_file)
        not_found_movie_ids = read_json_file(self.not_found_movie_ids_file)
        self.assertEqual(data, expected)
        self.assertEqual(not_found_movie_ids, [not_found_movie_id])

    def test_bundle_files(self):
        self.backup_file.unlink()
        self.metadata_file.unlink()
        max_movies_per_file = 1
        max_movies_per_bundled_file = 3

        # Expected outcome after fetching five new movies
        # [{fetched_data_1}]
        # [{fetched_data_2}]
        # [{fetched_data_3}]
        # [{fetched_data_4}]
        # [{fetched_data_5}]

        # Expected outcome after bundling and fetching two new movies
        # [{data_1}, {data_2}, {data_3}]
        # [{data_4}, {data_5}]
        # [{fetched_data_6}]
        # [{fetched_data_7}]

        # Expected outcome after bundling and fetching two new movies
        # [{data_1}, {data_2}, {data_3}]
        # [{data_4}, {data_5}, {data_6}]
        # [{data_7}]
        # {fetched_data_8}]
        # {fetched_data_9}]

        data_1 = self.movie_1_file_content
        data_2 = self.movie_2_file_content

        data_3 = data_1.copy()
        data_3["id"] = 3
        data_3["title"] = "Dummy Movie 3"

        data_4 = data_1.copy()
        data_4["id"] = 4
        data_4["title"] = "Dummy Movie 4"

        data_5 = data_1.copy()
        data_5["id"] = 5
        data_5["title"] = "Dummy Movie 5"

        data_6 = data_1.copy()
        data_6["id"] = 6
        data_6["title"] = "Dummy Movie 6"

        data_7 = data_1.copy()
        data_7["id"] = 7
        data_7["title"] = "Dummy Movie 7"

        data_8 = data_1.copy()
        data_8["id"] = 8
        data_8["title"] = "Dummy Movie 8"

        data_9 = data_1.copy()
        data_9["id"] = 9
        data_9["title"] = "Dummy Movie 9"

        metadata_file_1 = self.tmp_metadata_dir / "metadata_0001.jsonl"
        metadata_file_2 = self.tmp_metadata_dir / "metadata_0002.jsonl"
        metadata_file_3 = self.tmp_metadata_dir / "metadata_0003.jsonl"
        metadata_file_4 = self.tmp_metadata_dir / "metadata_0004.jsonl"
        metadata_file_5 = self.tmp_metadata_dir / "metadata_0005.jsonl"

        responses = [
            {"body": data_1},
            {"body": data_2},
            {"body": data_3},
            {"body": data_4},
            {"body": data_5},
        ]
        self.__class__.mock_fetch_latest_movie_id.return_value = 5
        with stub_requests(self.tmdb, responses=responses):
            self._collect_movie_metadata(
                max_movies_per_file=max_movies_per_file,
                max_movies_per_bundled_file=max_movies_per_bundled_file,
            )
        self.assertEqual(read_jsonl_file(metadata_file_1), [data_1])
        self.assertEqual(read_jsonl_file(metadata_file_2), [data_2])
        self.assertEqual(read_jsonl_file(metadata_file_3), [data_3])
        self.assertEqual(read_jsonl_file(metadata_file_4), [data_4])
        self.assertEqual(read_jsonl_file(metadata_file_5), [data_5])
        self.assertEqual(
            dir_size(self.tmp_backup_dir),
            dir_size(self.tmp_metadata_dir),
        )

        responses = [
            {"body": data_6},
            {"body": data_7},
        ]
        self.__class__.mock_fetch_latest_movie_id.return_value = 7
        with stub_requests(self.tmdb, responses=responses):
            self._collect_movie_metadata(
                max_movies_per_file=max_movies_per_file,
                max_movies_per_bundled_file=max_movies_per_bundled_file,
            )
        self.assertEqual(read_jsonl_file(metadata_file_1), [data_1, data_2, data_3])
        self.assertEqual(read_jsonl_file(metadata_file_2), [data_4, data_5])
        self.assertEqual(read_jsonl_file(metadata_file_3), [data_6])
        self.assertEqual(read_jsonl_file(metadata_file_4), [data_7])
        self.assertEqual(
            dir_size(self.tmp_backup_dir),
            dir_size(self.tmp_metadata_dir),
        )

        responses = [
            {"body": data_8},
            {"body": data_9},
        ]
        self.__class__.mock_fetch_latest_movie_id.return_value = 9
        with stub_requests(self.tmdb, responses=responses):
            self._collect_movie_metadata(
                max_movies_per_file=max_movies_per_file,
                max_movies_per_bundled_file=max_movies_per_bundled_file,
            )
        self.assertEqual(read_jsonl_file(metadata_file_1), [data_1, data_2, data_3])
        self.assertEqual(read_jsonl_file(metadata_file_2), [data_4, data_5, data_6])
        self.assertEqual(read_jsonl_file(metadata_file_3), [data_7])
        self.assertEqual(read_jsonl_file(metadata_file_4), [data_8])
        self.assertEqual(read_jsonl_file(metadata_file_5), [data_9])
        self.assertEqual(
            dir_size(self.tmp_backup_dir),
            dir_size(self.tmp_metadata_dir),
        )
