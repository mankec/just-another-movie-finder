from pathlib import Path

from django.core.management.base import BaseCommand

from core.files.utils import read_json_file
from movies.models import Country, Genre, Movie
from languages.constants import TVDB_SUPPORTED_LANGUAGES

class Command(BaseCommand):
    help = "Seed database."

    REMOTE_IDS = {
        "imdb": "IMDB",
        "tmdb": "TheMovieDB.com"
    }
    BATCH_SIZE = 1000

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
        country_objs = []
        for c in countries:
            country = Country(
                name=c["fields"]["name"],
                alpha_3=c["fields"]["alpha_3"],
                official_languages=c["fields"]["official_languages"],
            )
            country_objs.append(country)

        Country.objects.bulk_create(country_objs, batch_size=self.BATCH_SIZE)
        print("Done.")

        print("Creating genres...")
        genre_objs = []
        for g in genres:
            genre = Genre(
                tvdb_id=g["fields"]["tvdb_id"],
                name=g["fields"]["name"],
                slug=g["fields"]["slug"],
            )
            genre_objs.append(genre)

        Genre.objects.bulk_create(genre_objs, batch_size=self.BATCH_SIZE)
        print("Done.")

        print("Creating movies...")
        movie_genre_ids = {}
        movie_objs = []
        for m in movies:
            movie = Movie(
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
                genre_ids = [g["id"] for g in genres]

                movie_genre_ids[movie.tvdb_id] = genre_ids
            movie_objs.append(movie)

        Movie.objects.bulk_create(movie_objs, batch_size=self.BATCH_SIZE)
        print("Done.")

        print("Adding genres to movies...")
        for m in Movie.objects.all():
            if ids := movie_genre_ids.get(m.tvdb_id):
                m.genres.add(*ids)
        print("Done.")
