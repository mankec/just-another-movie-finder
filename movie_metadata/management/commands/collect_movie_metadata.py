import sys
import time
import shutil
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from http import HTTPStatus

from requests.exceptions import HTTPError
from django.core.management.base import BaseCommand

from movie_metadata.services import MovieMetadata
from core.constants import TIMEOUT_BEFORE_NEXT_REQUEST_SECONDS
from core.utils import flatten
from core.files.utils import (
    append_to_json_file,
    append_to_jsonl_file,
    create_empty_file,
    read_json_file,
    read_jsonl_file,
    dir_size,
)
from project.settings import TIME_ZONE


class Command(BaseCommand):
    DEFAULT_MAX_MOVIES_PER_FILE = 500
    DEFAULT_MAX_MOVIES_PER_BUNDLED_FILE = 10_000

    help = "Fetch movie metadata from TMDB and store it in JSON Lines."

    def add_arguments(self, parser):
        parser.add_argument('--metadata-dir', type=str, required=False, help='Directory you will save your metadata to.')
        parser.add_argument('--backup-dir', type=str, required=False, help='Directory that will act as a backup for you metadata directory.')
        parser.add_argument("--not-found-movie-ids-file", type=str, required=False, help="File that will be used to store ids of movies that haven't been found.")
        parser.add_argument('--max-movies-per-file', type=int, required=False, help='Max movies per file. Default is 500.')
        parser.add_argument('--max-movies-per-bundled-file', type=int, required=False, help='Max movies per bundled file. Default is 10 000.')

    def _movie_ids(self, fd):
        try:
            files = list(fd.iterdir())
            files_data = [read_jsonl_file(f) for f in files]
            return [d["id"] for d in flatten(files_data)]
        except Exception as error:
            print(f"Error while trying to fetch movie ids in {fd.name}: {error}")

    def _resolve_files(self):
        try:
            if self.movie_count == 0:
                return
            if len(read_jsonl_file(self.metadata_file)) < self.max_movies_per_file:
                return
            number = (self._last_metadata_file_number() + 1)
            self.metadata_file = self._metadata_file_name(number)
            self.backup_file = self.backup_dir / self.metadata_file.name
            create_empty_file(self.metadata_file)
            create_empty_file(self.backup_file)
        except (Exception, KeyboardInterrupt) as error:
            print("Error while resolving files: %s" % error)
            raise

    def _styled_output(self, message, level="SUCCESS"):
        style = getattr(self.style, level)
        print() # to make some distance between messages
        self.stdout.write(style(message))
        print()

    def _metadata_file_number(self, file):
        return (int(file.stem.split("_")[-1].lstrip("0")))

    def _last_metadata_file_number(self):
        last_metadata_file = self._sorted_files_by_name(
            self.metadata_dir.iterdir(),
            reverse=True
        )[0]
        return self._metadata_file_number(last_metadata_file)

    def _metadata_file_name(self, number):
        return self.metadata_dir / f"metadata_{number:04}.jsonl"

    def _sorted_files_by_name(self, files, *, reverse=False):
        if not files:
            return []
        return sorted(files, key=lambda file: self._metadata_file_number(file), reverse=reverse)

    def _eligible_metadata_file(self):
        files = self._sorted_files_by_name(self.metadata_dir.iterdir(), reverse=True)
        if not files:
            metadata_file = create_empty_file(self.metadata_dir / "metadata_0001.jsonl")
            return metadata_file

        last_metadata_file = files[0]
        if len(read_jsonl_file(last_metadata_file)) < self.max_movies_per_file:
            return last_metadata_file
        else:
            print("Creating new file to write to...")
            number = (self._last_metadata_file_number() + 1)
            name = self._metadata_file_name(number)
            metadata_file = create_empty_file(name)
            create_empty_file(self.backup_dir / metadata_file.name)
            return metadata_file

    def _is_file_corrupted(self, file):
        data = open(file, "r")
        try:
            json.load(data)
        except json.JSONDecodeError:
            return True
        except Exception as error:
            print("Error while checking if JSON file is corrupted: %s" % error)
            raise

    def _sync_dirs(self, src, dst):
        try:
            print(f"Syncing {dst.name} with {src.name}...")
            shutil.rmtree(dst)
            shutil.copytree(src, dst)
        except (Exception, KeyboardInterrupt) as error:
            print(f"Error while syncing '{src}' with '{dst}': {error}")
            raise

    def _check_dir_validity(self, fd):
        if not fd.exists():
            raise Exception(f"Directory {fd.name} doesn't exist.")
        if not fd.is_dir():
            raise NotADirectoryError(f"'{fd.name}' is not a directory.")

    def _check_if_metadata_and_backup_are_the_same_size(self):
        print("Checking if metadata and backup are the same size.")
        if dir_size(self.metadata_dir) != dir_size(self.backup_dir):
            print("Metadata is not the same size as backup.")
            self._sync_dirs(self.backup_dir, self.metadata_dir)
        else:
            print("Metadata is the same size as backup.")

    def _bundle_files(self):
        print("Bundling files...")
        files = [
            f for f in self._sorted_files_by_name(self.metadata_dir.iterdir())
            if len(read_jsonl_file(f)) < self.max_movies_per_bundled_file
        ]
        if len(files) <= 1:
            return
        files_data = [read_jsonl_file(f) for f in files]
        data = [d for d in flatten(files_data)]
        for file in files:
            file.unlink()
        while data:
            number = (
                1 if not list(self.metadata_dir.iterdir())
                else (self._last_metadata_file_number() + 1)
            )
            append_to_file = self._metadata_file_name(number)
            create_empty_file(append_to_file)

            sliced_data = data[:self.max_movies_per_bundled_file]
            append_to_jsonl_file(sliced_data, append_to_file)

            data = data[self.max_movies_per_bundled_file:]
        self._sync_dirs(self.metadata_dir, self.backup_dir)

    def _setUp(self, options):
        self.metadata_dir = (Path(options["metadata_dir"])
            if options.get("metadata_dir")
            else Path("movie_metadata/metadata")
        )
        self.metadata_dir = (Path(options["metadata_dir"])
            if options.get("metadata_dir")
            else Path("movie_metadata/metadata")
        )
        self.backup_dir = (Path(options["backup_dir"])
            if options.get("backup_dir")
            else Path("movie_metadata/backup")
        )
        self.not_found_movie_ids_file = (Path(options["not_found_movie_ids_file"])
            if options.get("not_found_movie_ids_file")
            else Path("movie_metadata/not_found_movie_ids.json")
        )
        self.max_movies_per_file = (
            options["max_movies_per_file"] or
            self.__class__.DEFAULT_MAX_MOVIES_PER_FILE
        )
        self.max_movies_per_bundled_file = (
            options["max_movies_per_bundled_file"] or
            self.__class__.DEFAULT_MAX_MOVIES_PER_BUNDLED_FILE
        )

        self._check_dir_validity(self.metadata_dir)
        self._check_dir_validity(self.backup_dir)

        self._check_if_metadata_and_backup_are_the_same_size()

        self._bundle_files()

        self.metadata_file = self._eligible_metadata_file()
        self.backup_file = self.backup_dir / self.metadata_file.name

        print("Getting movie ids...")
        self.movie_ids_in_backup = self._movie_ids(self.backup_dir)
        self.movie_ids_in_metadata = self._movie_ids(self.metadata_dir)
        self.not_found_movie_ids = read_json_file(self.not_found_movie_ids_file)
        self.movie_count = len(self.movie_ids_in_metadata)

    def handle(self, *_args, **options):
        try:
            tmdb = MovieMetadata.TMDB()
            self._setUp(options)

            movie_id = max(self.movie_ids_in_metadata, default=0) + 1
            movie_count_at_start = self.movie_count
            now = datetime.now(ZoneInfo(TIME_ZONE)).strftime("%D %H:%M")
            while movie_id <= tmdb.latest_movie_id:
                if (
                    movie_id in self.movie_ids_in_metadata or
                    movie_id in self.not_found_movie_ids
                ):
                    print("")
                    print(f"Skipping movie with ID {movie_id}")
                    print("")
                    movie_id += 1
                    continue
                try:
                    self._resolve_files()
                    print("--------------------------------------")
                    print(f"Started at {now}")
                    print(f"Latest movie ID: {tmdb.latest_movie_id}")
                    print(f"Movie ID: {movie_id}")
                    print(f"Fetching...")

                    data = tmdb.fetch_details(movie_id)

                    print(f"Fetched {data["title"]}")
                    print(f"Collected in this session: {(self.movie_count + 1) - movie_count_at_start}")
                    print(f"Movies collected: {self.movie_count + 1}")

                    print(f"Saving to {self.metadata_file}...")
                    append_to_jsonl_file(data, self.metadata_file)

                    print("Copying to backup...")
                    shutil.copy(self.metadata_file, self.backup_file)
                    print("Copied.")
                    self.movie_count += 1
                    movie_id += 1
                    time.sleep(TIMEOUT_BEFORE_NEXT_REQUEST_SECONDS)
                except HTTPError as error:
                    response = error.response
                    if response.status_code == HTTPStatus.NOT_FOUND.value:
                        if movie_id not in self.not_found_movie_ids:
                            append_to_json_file(movie_id, self.not_found_movie_ids_file)
                        movie_id += 1
                        time.sleep(TIMEOUT_BEFORE_NEXT_REQUEST_SECONDS)
                        continue
                    else:
                        self._styled_output(message, level="ERROR")
                        sys.exit(1)
                except KeyboardInterrupt:
                    print("Gracefully stopping...")
                    sys.exit(1)
                except Exception as error:
                    message = str(error)
                    self._styled_output(message, level="ERROR")
                    sys.exit(1)
            print(f"Finished at {datetime.now(ZoneInfo(TIME_ZONE)).strftime("%D %H:%M")}.")
        except Exception as error:
            print("Error while handling `collect_movie_metadata` command: %s" % error)
            sys.exit(1)
