from pathlib import Path

from django.core.management.base import BaseCommand

from project.utils.file_utils import read_file
from movies.models import Movie

class Command(BaseCommand):
    help = "Seed database."

    def _remote_id(self, remote_ids, *, source_name):
        return next(
            (
                remote_id["id"] for remote_id in remote_ids
                if remote_id["sourceName"] == source_name
            ),
            None
        )

    def handle(self, *_args, **_options):
        seeds_dir = Path("movies/seeds")
        movies = read_file(seeds_dir / "movies.json")

        for movie in movies:
            print(f"Creating movie with id {movie["id"]}")

                # if movie["id"] == 148:
                #     breakpoint()
            movie = Movie.objects.create(
                title=movie["name"],
                slug=movie["slug"],
                image =movie["image"],
                runtime=movie["runtime"],
                status=movie["status"]["name"],
                last_updated=movie["lastUpdated"],
                keep_updated=movie["status"]["keepUpdated"],
                year=int(movie["year"]),
                tvdb_id=movie["id"],
                imdb_id=self._remote_id(movie["remoteIds"], source_name="IMDB"),
                tmdb_id=self._remote_id(movie["remoteIds"], source_name="TheMovieDB.com"),
                budget=int(float(movie["budget"])) if movie["budget"] else None,
                box_office=int(float(movie["boxOffice"])) if movie["boxOffice"] else None,
                country=movie["originalCountry"],
                language=movie["originalLanguage"],
            )
