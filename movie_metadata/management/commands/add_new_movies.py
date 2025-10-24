import sys
import time
from datetime import datetime
from http import HTTPStatus

from requests.exceptions import HTTPError
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db import transaction

from core.constants import TIMEOUT_BEFORE_NEXT_REQUEST_SECONDS, BULK_CREATE_BATCH_SIZE
from movies.models import Movie, Person, Cast, Crew
from movie_metadata.services import MovieMetadata


class Command(BaseCommand):
    help = "Fetch and add new movies to database. Adult movies are skipped."

    MAX_MOVIE_OBJS_IN_SINGLE_RUN = 1000

    def handle(self, *_args, **_options):
        try:
            tmdb = MovieMetadata.TMDB()
            movie_genre_ids = {}
            person_ids = {}
            movie_objs = []
            cast_objs = []
            crew_objs = []
            movie_id = Movie.objects.last().id + 1 if Movie.objects.last() else 1

            while movie_id <= tmdb.latest_movie_id:
                try:
                    print(f"Fetching movie with id={movie_id}/{tmdb.latest_movie_id}")
                    data = tmdb.fetch_details(movie_id)

                    if data["adult"]:
                        movie_id += 1
                        continue

                    release_date = data["release_date"]
                    year = datetime.strptime(release_date, "%Y-%m-%d").year if data["release_date"] else None

                    movie_obj = Movie(
                        id=data["id"],
                        backdrop_path=data["backdrop_path"],
                        budget=data["budget"],
                        imdb_id=data["imdb_id"],
                        origin_country=data["origin_country"],
                        original_language=data["original_language"],
                        original_title=data["original_title"],
                        overview=data["overview"],
                        poster_path=data["poster_path"],
                        release_date=release_date,
                        year=year,
                        revenue=data["runtime"],
                        runtime=data["runtime"],
                        spoken_languages=data["spoken_languages"],
                        status=data["status"],
                        tagline=data["tagline"],
                        title=data["title"],
                        slug=slugify(data["title"]),
                        vote_average=data["vote_average"],
                        vote_count=data["vote_count"],
                        backdrops=data["images"]["backdrops"] if data.get("images") else [],
                        logos=data["images"]["logos"] if data.get("images") else [],
                        posters=data["images"]["posters"] if data.get("images") else [],
                        keywords=data["keywords"]["keywords"] if data.get("keywords") else [],
                        recommendations=data["recommendations"]["results"] if data.get("recommendations") else [],
                        similar=data["similar"]["results"] if data.get("similar") else [],
                    )
                    movie_objs.append(movie_obj)

                    if genres := data["genres"]:
                        genre_ids = [g["id"] for g in genres]
                        movie_genre_ids[movie_obj.id] = genre_ids

                    cast = data["credits"]["cast"] if data.get("credits") else []
                    if cast:
                        for c in cast:
                            person_ids[c["id"]] = {k: c.get(k) for k in Person.DEFAULTS}
                            cast_obj = Cast(
                                credit_id=c["credit_id"],
                                character=c["character"],
                                movie=movie_obj,
                                person_id=c["id"],
                            )
                            cast_objs.append(cast_obj)

                    crew = data["credits"]["crew"] if data.get("credits") else []
                    if crew:
                        for c in crew:
                            person_ids[c["id"]] = {k: c.get(k) for k in Person.DEFAULTS}
                            crew_obj = Crew(
                                credit_id=c["credit_id"],
                                department=c["department"],
                                job=c["job"],
                                movie=movie_obj,
                                person_id=c["id"],
                            )
                            crew_objs.append(crew_obj)

                    if len(movie_objs) == self.__class__.MAX_MOVIE_OBJS_IN_SINGLE_RUN:
                        break

                    movie_id += 1
                    time.sleep(TIMEOUT_BEFORE_NEXT_REQUEST_SECONDS)
                except HTTPError as error:
                    response = error.response
                    if response.status_code == HTTPStatus.NOT_FOUND.value:
                        movie_id += 1
                        time.sleep(TIMEOUT_BEFORE_NEXT_REQUEST_SECONDS)
                        continue
                    else:
                        print(f"Unexpected HTTP error: {error}")
                        sys.exit(1)
                except Exception as error:
                    print(f"Unexpected exception while fetching movies: {error}")
                    sys.exit(1)

            with transaction.atomic():
                print(f"Finished fetching. Creating {len(movie_objs)} new movies.")
                Movie.objects.bulk_create(movie_objs, batch_size=BULK_CREATE_BATCH_SIZE)
                print("Done.")

                print("Adding genres to movies...")
                for m in movie_objs:
                    if ids := movie_genre_ids.get(m.id):
                        m.genres.add(*ids)
                print("Done.")

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
                print(f"Creating {len(person_objs)} new persons.")
                Person.objects.bulk_create(person_objs, batch_size=BULK_CREATE_BATCH_SIZE)
                print("Done.")

                print(f"Creating {len(cast_objs)} new casts.")
                Cast.objects.bulk_create(cast_objs, batch_size=BULK_CREATE_BATCH_SIZE)
                print("Done.")

                print(f"Creating {len(crew_objs)} new crews.")
                Crew.objects.bulk_create(crew_objs, batch_size=BULK_CREATE_BATCH_SIZE)
                print("Done.")
        except Exception as error:
            print(f"Unexpected exception: {error}")
            sys.exit(1)
