import sys
import time
from datetime import datetime
from http import HTTPStatus

from requests.exceptions import HTTPError
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from core.constants import TIMEOUT_BEFORE_NEXT_REQUEST_SECONDS, BULK_CREATE_BATCH_SIZE
from movies.models import Movie
from movie_metadata.services import MovieMetadata


class Command(BaseCommand):
    help = "Fetch and add new movies to database."

    def handle(self, *_args, **_options):
        try:
            tmdb = MovieMetadata.TMDB()
            movie_objs = []
            movie_id = Movie.objects.last().id + 1 if Movie.objects.last() else 1

            while movie_id <= tmdb.latest_movie_id:
                try:
                    data = tmdb.fetch_details(movie_id)
                    release_date = data["release_date"]
                    year = datetime.strptime(release_date, "%Y-%m-%d").year

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

                    movie_id += 1
                    time.sleep(TIMEOUT_BEFORE_NEXT_REQUEST_SECONDS)
                except HTTPError as error:
                    response = error.response
                    if response.status_code == HTTPStatus.NOT_FOUND.value:
                        movie_id += 1
                        time.sleep(TIMEOUT_BEFORE_NEXT_REQUEST_SECONDS)
                        continue
                    else:
                        sys.exit(1)
                except Exception as error:
                    sys.exit(1)
            Movie.objects.bulk_create(movie_objs, batch_size=BULK_CREATE_BATCH_SIZE)
        except Exception as error:
            sys.exit(1)
