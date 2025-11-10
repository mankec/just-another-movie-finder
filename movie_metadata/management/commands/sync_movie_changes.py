import sys
import time
import ast
from http import HTTPStatus
from pathlib import Path

from requests.exceptions import HTTPError
from django.core.management.base import BaseCommand

from core.constants import TIMEOUT_BEFORE_NEXT_REQUEST_SECONDS

from movies.models import Movie
from movie_metadata.services import MovieMetadata

class Command(BaseCommand):
    help = "Fetch movie changes from TMDB and update them in database."

    def _to_dict(self, value):
        try:
            return ast.literal_eval(value)
        except Exception:
            return {}

    def handle(self, *_args, **_options):
        try:
            tmdb = MovieMetadata.TMDB()
            movies = Movie.objects.order_by("id").filter(id__gt=1518780)

            for movie in movies:
                try:
                    if (
                        movie.similar == [] and
                        movie.recommendations == [] and
                        movie.logos == [] and
                        movie.backdrops == [] and
                        movie.posters
                    ):
                        continue

                    try:
                        movie.similar != [] and ast.literal_eval(movie.similar)
                        movie.recommendations != [] and ast.literal_eval(movie.recommendations)
                        movie.logos != [] and ast.literal_eval(movie.logos)
                        movie.backdrops != [] and ast.literal_eval(movie.backdrops)
                        movie.posters != [] and ast.literal_eval(movie.posters)
                        print(f"Movie with id={movie.id} is valid")
                    except Exception as error:
                        breakpoint()
                        data = tmdb.fetch_details(movie.id)

                        if data["adult"]:
                            movie.delete()
                            continue

                        print(f"Updating movie with id={movie.id}")

                        images = data.get("images")

                        movie.logos = images["logos"] if images else []
                        movie.posters = images["posters"] if images else []
                        movie.backdrops = images["backdrops"] if images else []
                        movie.recommendations = data["recommendations"]["results"] if data.get("recommendations") else []
                        movie.similar = data["similar"]["results"] if data.get("similar") else []
                        movie.save()
                        time.sleep(TIMEOUT_BEFORE_NEXT_REQUEST_SECONDS)
                except HTTPError as error:
                    response = error.response
                    if response.status_code == HTTPStatus.NOT_FOUND.value:
                        movie.delete()
                        time.sleep(TIMEOUT_BEFORE_NEXT_REQUEST_SECONDS)
                        continue
                    else:
                        print(f"Unexpected HTTP error while updating movies: {error}")
                        sys.exit(1)
                except Exception as error:
                    print(f"Unexpected exception while updating movies: {error}")
                    sys.exit(1)
        except Exception as error:
            print(f"Unexpected exception: {error}")
            sys.exit(1)
