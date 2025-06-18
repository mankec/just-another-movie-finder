from pathlib import Path

from django.core.management.base import BaseCommand

from core.file.utils import read_json_file
from movies.models import Country, Genre, Movie
from movies.constants import TVDB_SUPPORTED_LANGUAGES

class Command(BaseCommand):
    help = "Seed database."

    REMOTE_IDS = {
        "imdb": "IMDB",
        "tmdb": "TheMovieDB.com"
    }

    def _remote_id(self, remote_ids, *, source_name):
        return next(
            (
                remote_id["id"] for remote_id in remote_ids
                if remote_id["sourceName"] == source_name
            ),
            None
        )

    def handle(self, *_args, **_options):
        seeds_dir = Path("db/seeds")
        fixtures_dir = Path("db/fixtures")
        movies = read_json_file(seeds_dir / "movies.json")
        genres = read_json_file(fixtures_dir / "genres.json")
        countries = read_json_file(fixtures_dir / "countries.json")

        print("Creating countries...")
        for c in countries:
            Country.objects.create(
                name=c["fields"]["name"],
                alpha_3=c["fields"]["alpha_3"],
                official_languages=c["fields"]["official_languages"],
            )
        print("Done.")

        print("Creating genres...")
        for g in genres:
            Genre.objects.create(
                tvdb_id=g["fields"]["tvdb_id"],
                name=g["fields"]["name"],
                slug=g["fields"]["slug"],
            )
        print("Done.")

        print("Creating movies...")
        for m in movies:
            movie = Movie.objects.create(
                title=m["name"],
                slug=m["slug"],
                poster =m["image"],
                runtime=m["runtime"],
                status=m["status"]["name"],
                last_updated=m["lastUpdated"],
                keep_updated=m["status"]["keepUpdated"],
                year=int(m["year"]),
                tvdb_id=m["id"],
                imdb_id=self._remote_id(
                    m["remoteIds"],
                    source_name=self.REMOTE_IDS["imdb"]
                ),
                tmdb_id=self._remote_id(
                    m["remoteIds"],
                    source_name=self.REMOTE_IDS["tmdb"]
                ),
                budget=int(float(m["budget"])) if m["budget"] else None,
                box_office=int(float(m["boxOffice"])) if m["boxOffice"] else None,
                country=Country.objects.get(alpha_3=m["originalCountry"]),
                language=TVDB_SUPPORTED_LANGUAGES[m["originalLanguage"]]["name"],
                language_alpha_3=m["originalLanguage"],
            )
            if genres := m["genres"]:
                for g in genres:
                    genre = Genre.objects.get(pk=g["id"])
                    movie.genres.add(genre)
            movie.save()
        print("Done.")
