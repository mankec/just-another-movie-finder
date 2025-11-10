import sys
import ast
from http import HTTPStatus
from pathlib import Path

from requests.exceptions import HTTPError
from django.core.management.base import BaseCommand

from core.constants import TMDB_ACTIONS
from movies.languages.constants import LANGUAGES

from movies.models import Movie, Genre, Cast, Crew
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
            movie_ids = tmdb.fetch_changed_movie_ids()
            movies = Movie.objects.filter(id__in=movie_ids)
            field_map = {
                "imdb_id": "imdb_id",
                "backdrop_path": "backdrop_path",
                "budget": "budget",
                "genres": "genres",
                "original_language": "original_language",
                "original_title": "original_title",
                "overview": "overview",
                "popularity": "popularity",
                "poster_path": "poster_path",
                "release_date": "release_date",
                "revenue": "revenue",
                "runtime": "runtime",
                "spoken_languages": "spoken_languages",
                "status": "status",
                "tagline": "tagline",
                "title": "title",
                "vote_average": "vote_average",
                "vote_count": "vote_count",
                "genres": "genres",
                "cast": "cast",
                "crew": "crew_set.all",
                "images": "images",
                "plot_keywords": "keywords",
                "character_names": "character_names"
            }
            image_types = {
                "poster": "poster",
                "backdrop": "backdrop",
                "logo": "logo",
                "title_logo": "title_logo",
            }
            for movie in movies:
                movie_changes = tmdb.fetch_movie_changes(movie.id)

                for change in movie_changes:
                    key = change["key"]
                    if key not in field_map.keys():
                        continue

                    if key != field_map["images"]:
                        field = getattr(movie, field_map[key])

                        if type(field) == list:
                            field = list(map(ast.literal_eval, field))

                    for item in change["items"]:
                        action = item["action"]
                        value = item.get("value")
                        original_value = item.get("original_value")

                        if key == field_map["genres"]:
                            if action == TMDB_ACTIONS["added"]:
                                movie.genres.add(value["id"])
                            elif action == TMDB_ACTIONS["deleted"]:
                                movie.genres.remove(original_value["id"])
                            else:
                                raise Exception(f"Unknown action while updating movie's genres: {action}.")
                        elif key == field_map["cast"]:
                            if action == TMDB_ACTIONS["added"]:
                                Cast.objects.create(
                                    credit_id=value["credit_id"],
                                    character=value["character"],
                                    movie=movie,
                                    person_id=value["id"],
                                )
                            elif action == TMDB_ACTIONS["deleted"]:
                                Cast.objects.filter(credit_id=original_value["credit_id"]).delete()
                            else:
                                raise Exception(f"Unknown action while updating movie's cast: {action}.")
                            field = movie.cast_set
                        elif key == field_map["crew"]:
                            if action == TMDB_ACTIONS["added"]:
                                Crew.objects.create(
                                    credit_id=value["credit_id"],
                                    department=value["department"],
                                    job=value["job"],
                                    movie=movie,
                                    person_id=value["id"],
                                )
                            elif action == TMDB_ACTIONS["deleted"]:
                                Crew.objects.filter(credit_id=original_value["credit_id"]).delete()
                            else:
                                raise Exception(f"Unknown action while updating movie's crew: {action}.")
                        elif key == field_map["images"]:
                            if value:
                                image_type = list(value.keys())[0]
                            else:
                                image_type = list(original_value.keys())[0]

                            if image_type == image_types["poster"]:
                                field = movie.posters
                            elif image_type == image_types["backdrop"]:
                                field = movie.backdrops
                            elif image_type == image_types["logo"] or image_type == image_types["title_logo"]:
                                field = movie.logos
                            else:
                                raise ValueError("Unknown image type")

                            field = list(map(ast.literal_eval, field))

                            if action == TMDB_ACTIONS["added"]:
                                field.append(value[image_type])
                                field = [str(x) for x in field]
                                if image_type == image_types["poster"]:
                                    movie.posters = field
                                elif image_type == image_types["backdrop"]:
                                    movie.backdrops = field
                                else:
                                    movie.logos = field
                            elif action == TMDB_ACTIONS["updated"]:
                                file_path = original_value[image_type]["file_path"]
                                image = next(
                                    (x for x in field if x["file_path"] == file_path),
                                    None
                                )
                                if image:
                                    for k, v in value[image_type].items():
                                        image[k] = v

                                    # TODO: Very dirty, should be fixed. Remove `models.CharField(max_length=MAX_LENGTH)` for ArrayField where you store dicts instead of strings
                                    field = [str(x) for x in field]
                                    if image_type == image_types["poster"]:
                                        movie.posters = field
                                    elif image_type == image_types["backdrop"]:
                                        movie.backdrops = field
                                    else:
                                        movie.logos = field
                            elif action == TMDB_ACTIONS["deleted"]:
                                field = [x for x in field if x["file_path"] != original_value[image_type]["file_path"]]
                                field = [str(x) for x in field]
                                if image_type == image_types["poster"]:
                                    movie.posters = field
                                elif image_type == image_types["backdrop"]:
                                    movie.backdrops = field
                                else:
                                    movie.logos = field
                            else:
                                raise ValueError(f"Unknown action while updating movie's {image_type}: {action}")
                        elif key == field_map["spoken_languages"]:
                            if len(change["items"]) > 1:
                                raise ValueError("There should only be one item when updating movie's spoken languages.")

                            if action == TMDB_ACTIONS["added"]:
                                for iso_639_1 in value:
                                    field.append(LANGUAGES[iso_639_1])
                            elif action == TMDB_ACTIONS["updated"]:
                                field = []
                                for iso_639_1 in value:
                                    field.append(LANGUAGES[iso_639_1])
                            elif action == TMDB_ACTIONS["deleted"]:
                                for iso_639_1 in original_value:
                                    field = [x for x in field if x != LANGUAGES[iso_639_1]]
                            else:
                                raise Exception(f"Unknown action while updating movie's spoken languages: {action}")
                        elif key == field_map["plot_keywords"]:
                            if action == TMDB_ACTIONS["added"]:
                                field.append(value)
                            elif action == TMDB_ACTIONS["deleted"]:
                                field = [x for x in field if x != value]
                            else:
                                raise Exception(f"Unknown action while updating movie's keywords: {action}")
                        else:
                            if action == TMDB_ACTIONS["updated"]:
                                field = value
                            elif action == TMDB_ACTIONS["deleted"]:
                                field = None
                            else:
                                raise ValueError(f"Unknown action while updating movie's {field_map[key]}: {action}")
                movie.save()
        except Exception as error:
            print(f"Unexpected exception: {error}")
            sys.exit(1)
