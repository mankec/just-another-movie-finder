from pathlib import Path
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from core.files.utils import read_json_file, read_jsonl_file
from movies.models import Genre, Movie, Cast, Crew, Person

class Command(BaseCommand):
    help = "Seed database."

    REMOTE_IDS = {
        "imdb": "IMDB",
        "tmdb": "TheMovieDB.com"
    }
    BATCH_SIZE = 1000

    def handle(self, *_args, **_options):
        seeds_dir = Path("db/seeds")
        fixtures_dir = Path("db/fixtures")
        movies = read_jsonl_file(seeds_dir / "movies.jsonl")
        genres = read_json_file(fixtures_dir / "genres.json")

        print("Creating genres...")
        genre_objs = []
        for g in genres:
            genre_obj = Genre(
                id=g["pk"],
                name=g["fields"]["name"],
            )
            genre_objs.append(genre_obj)

        Genre.objects.bulk_create(genre_objs, batch_size=self.BATCH_SIZE)

        import sys; sys.exit(1)
        print("Done.")

        print("Creating movies...")
        movie_genre_ids = {}
        person_ids = {}
        movie_objs = []
        cast_objs = []
        crew_objs = []
        for m in movies:
            if m["adult"]:
                breakpoint()
            movie_obj = Movie(
                id=m["id"],
                backdrop_path=m["backdrop_path"],
                budget=m["budget"],
                imdb_id=m["imdb_id"],
                origin_country=m["origin_country"],
                original_language=m["original_language"],
                original_title=m["original_title"],
                overview=m["overview"],
                poster_path=m["poster_path"],
                release_date=release_date,
                year=year,
                revenue=m["runtime"],
                runtime=m["runtime"],
                spoken_languages=m["spoken_languages"],
                status=m["status"],
                tagline=m["tagline"],
                title=m["title"],
                slug=slugify(m["title"]),
                vote_average=m["vote_average"],
                vote_count=m["vote_count"],
                backdrops=m["images"]["backdrops"] if m.get("images") else [],
                logos=m["images"]["logos"] if m.get("images") else [],
                posters=m["images"]["posters"] if m.get("images") else [],
                keywords=m["keywords"]["keywords"] if m.get("keywords") else [],
                recommendations=m["recommendations"]["results"] if m.get("recommendations") else [],
                similar=m["similar"]["results"] if m.get("similar") else [],
            )
            if genres := m["genres"]:
                genre_ids = [g["id"] for g in genres]

                movie_genre_ids[movie_obj.id] = genre_ids
            cast = m["credits"]["cast"] if m.get("credits") else []
            if cast:
                for c in cast:
                    person_ids[c["id"]] = {k: c[k] for k in Person.DEFAULTS}
                    cast_obj = Cast(
                        credit_id=c["credit_id"],
                        character=c["character"],
                        movie=movie_obj,
                        person_id=c["id"],
                    )
                    cast_objs.append(cast_obj)
            crew = m["credits"]["crew"] if m.get("credits") else []
            if crew:
                for c in crew:
                    person_ids[c["id"]] = {k: c[k] for k in Person.DEFAULTS}
                    crew_obj = Crew(
                        credit_id=c["credit_id"],
                        department=c["department"],
                        job=c["job"],
                        movie=movie_obj,
                        person_id=c["id"],
                    )
                    crew_objs.append(crew_obj)
            movie_objs.append(movie_obj)

        Movie.objects.bulk_create(movie_objs, batch_size=self.BATCH_SIZE)
        print("Done.")

        print("Adding genres to movies...")
        for m in Movie.objects.all():
            if ids := movie_genre_ids.get(m.id):
                m.genres.add(*ids)
        print("Done.")

        print("Creating persons...")
        existing_person_ids = set(
            Person.objects.filter(id__in=person_ids.keys()).values_list("id", flat=True)
        )
        person_objs = [
            Person(
                id=k,
                **v
            )
            for k, v in person_ids.items()
            if k not in existing_person_ids
        ]
        Person.objects.bulk_create(person_objs, batch_size=self.BATCH_SIZE)
        print("Done.")

        print("Creating cast...")
        Cast.objects.bulk_create(cast_objs, batch_size=self.BATCH_SIZE)
        print("Done.")

        print("Creating crew...")
        Crew.objects.bulk_create(crew_objs, batch_size=self.BATCH_SIZE)
        print("Done.")
