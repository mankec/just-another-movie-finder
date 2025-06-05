import sys
import time
import shutil
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter

from django.core.management.base import BaseCommand

from movie_metadata.services.base import MovieMetadata
from project.utils import (
    append_to_json_file,
    create_empty_json_file,
    read_file,
    flatten
)
from project.settings import TIME_ZONE
from project.constants import NOT_FOUND_MESSAGE


class Command(BaseCommand):
    DEFAULT_MAX_MOVIES_PER_FILE = 2500
    TIMEOUT_BEFORE_NEXT_REQUEST = 1.5

    help = "Fetch movie metadata from TVDB and store it in JSON."

    def __init__(self):
        super().__init__()
        self.metadata_dir = ...
        self.backup_dir = ...
        self.metadata_files = ...
        self.backup_files = ...
        self.metadata_file = ...
        self.backup_file = ...
        self.movie_ids_in_backup = ...
        self.movie_ids_in_metadata = ...
        self.movie_count = ...

    def add_arguments(self, parser):
        parser.add_argument('--metadata-dir-path', type=str, required=True, help='Directory you will save your metadata to.')
        parser.add_argument('--backup-dir-path', type=str, required=True, help='Directory that will act as a backup for you metadata directory.')
        parser.add_argument('--max-movies-per-file', type=int, required=False, help='Max movies per file. Default is 2500.')

    def _movie_ids(self, *, directory):
        try:
            files = list(directory.iterdir())
            files_data = [read_file(f) for f in files]
            return [d["id"] for d in flatten(files_data)]
        except Exception as error:
            print(f"Error while trying to fetch movie ids in {directory.name}: {error}")

    def _resolve_files(self):
        try:
            if self.movie_count == 0:
                return
            if self.movie_count % self.max_movies_per_file != 0:
                return
            number = (self._last_metadata_file_number() + 1)
            self.metadata_file = self._metadata_file_name(number)
            self.backup_file = self.backup_dir / self.metadata_file.name
            create_empty_json_file(self.metadata_file, json_type="arr")
            create_empty_json_file(self.backup_file, json_type="arr")
        except (Exception, KeyboardInterrupt) as error:
            print("Error while resolving files: %s" % error)
            raise

    def _remove_redundant_data(self, data):
        try:
            redundant = ["nameTranslations", "overviewTranslations", "aliases", "score", "trailers", "releases", "artworks", "boxOfficeUS", "audioLanguages", "subtitleLanguages", "lists", "contentRatings", "production_countries", "spoken_languages", "first_release"]

            for x in redundant:
                del data[x]
        except (Exception, KeyboardInterrupt) as error:
            print("Error while removing redundant data: %s" % error)
            raise

    def _styled_output(self, message, level="SUCCESS"):
        style = getattr(self.style, level)
        print() # to make some distance between messages
        self.stdout.write(style(message))
        print()

    def _metadata_file_number(self, file):
        return (int(file.stem.split("_")[-1].lstrip("0")))

    def _last_metadata_file_number(self):
        last_metadata_file = self._sorted_files_by_name(self.metadata_files, reverse=True)[0]
        return self._metadata_file_number(last_metadata_file)

    def _metadata_file_name(self, number):
        return self.metadata_dir / f"metadata_{number:04}.json"

    def _sorted_files_by_name(self, files, *, reverse=False):
        if not files:
            return []
        return sorted(files, key=lambda file: self._metadata_file_number(file), reverse=reverse)

    def _find_eligible_metadata_file(self):
        files = self._sorted_files_by_name(self.metadata_files)
        if not files:
            metadata_file = create_empty_json_file(
                self.metadata_dir / "metadata_0001.json",
                json_type="arr"
            )
            return metadata_file
        eligible_file = next(
            (f for f in files if len(read_file(f)) < self.max_movies_per_file),
            None
        )
        if not eligible_file:
            print("Creating new file to write to...")
            number = (self._last_metadata_file_number() + 1)
            name = self._metadata_file_name(number)
            metadata_file = create_empty_json_file(name, json_type="arr")
            create_empty_json_file(self.backup_dir / metadata_file.name, json_type="arr")
            return metadata_file
        return eligible_file

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
            shutil.copytree(src, dst, dirs_exist_ok=True)
            self.metadata_files = list(self.metadata_dir.iterdir())
            self.backup_files = list(self.backup_dir.iterdir())
        except (Exception, KeyboardInterrupt) as error:
            print(f"Error while syncing '{src}' with '{dst}': {error}")
            raise

    def _check_dir_validity(self, fd):
        if not fd.exists():
            raise Exception(f"Directory {fd.name} doesn't exist.")
        if not fd.is_dir():
            raise NotADirectoryError(f"'{fd.name}' is not a directory.")

    def _check_if_metadata_dir_is_corrupted(self):
        print("Checking if metadata is corrupted...")
        corrupted_files = [f for f in self.metadata_files if self._is_file_corrupted(f)]
        if corrupted_files:
            print(f"Metadata is corrupted.")
            self._sync_dirs(self.backup_dir, self.metadata_dir)
        else:
            print(f"Metadata is not corrupted.")

    def _setUp(self, options):
        self.metadata_dir = Path(options["metadata_dir_path"])
        self.backup_dir = Path(options["backup_dir_path"])
        self.max_movies_per_file = options["max_movies_per_file"] or self.__class__.DEFAULT_MAX_MOVIES_PER_FILE

        self._check_dir_validity(self.metadata_dir)
        self._check_dir_validity(self.backup_dir)

        self.metadata_files = list(self.metadata_dir.iterdir())
        self.backup_files = list(self.backup_dir.iterdir())
        self.metadata_file = self._find_eligible_metadata_file()
        self.backup_file = self.backup_dir / self.metadata_file.name
        self.not_found_movie_ids_file = Path("movie_metadata/not_found_movie_ids.json")

        self._check_if_metadata_dir_is_corrupted()

        self.movie_ids_in_backup = self._movie_ids(directory=self.backup_dir)
        self.movie_ids_in_metadata = self._movie_ids(directory=self.metadata_dir)
        self.not_found_movie_ids = read_file(self.not_found_movie_ids_file)
        self.movie_count = len(self.movie_ids_in_metadata)

    def handle(self, *_args, **options):
        try:
            tvdb = MovieMetadata.TVDB()
            self._setUp(options)

            movie_id = max(self.movie_ids_in_metadata, default=0) + 1
            movie_count_at_start = self.movie_count
            now = datetime.now(ZoneInfo(TIME_ZONE)).strftime("%D %H:%M")
            while self.movie_count != tvdb.total_movies:
                if movie_id in self.movie_ids_in_metadata:
                    continue
                try:
                    self._resolve_files()

                    print("--------------------------------------")
                    print(f"Started at {now}")  
                    print(f"Number of movies to collect: {tvdb.total_movies}")
                    print(f"Movie ID: {movie_id}")
                    print(f"Fetching...")

                    response = tvdb.fetch_extended(movie_id)
                    data = response["data"]

                    print(f"Fetched {data["name"]}")
                    print(f"Collected in this session: {(self.movie_count + 1) - movie_count_at_start}")
                    print(f"Movies collected: {self.movie_count + 1}")

                    self._remove_redundant_data(data)

                    print(f"Saving to {self.metadata_file}...")
                    append_to_json_file(data, self.metadata_file)

                    print("Copying to backup...")
                    shutil.copy(self.metadata_file, self.backup_file)
                except Exception as error:
                    message = str(error)
                    if message == NOT_FOUND_MESSAGE:
                        if movie_id not in self.not_found_movie_ids:
                            append_to_json_file(movie_id, self.not_found_movie_ids_file)
                        time.sleep(self.__class__.TIMEOUT_BEFORE_NEXT_REQUEST)
                        continue
                    else:
                        self._styled_output(message, level="ERROR")
                        break
                except KeyboardInterrupt:
                    print("Gracefully stopping...")
                    break
                finally:
                    movie_id += 1
                self.movie_count += 1
                time.sleep(self.__class__.TIMEOUT_BEFORE_NEXT_REQUEST)
            print(f"Finished at {datetime.now(ZoneInfo(TIME_ZONE)).strftime("%D %H:%M")}.")
        except Exception as error:
            print("Error while handling `collect_movie_metadata` command: %s" % error)
            sys.exit(1)
