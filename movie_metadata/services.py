import ast
from http import HTTPMethod, HTTPStatus

from environs import Env
from requests.exceptions import HTTPError

from project.settings import USER_AGENT
from core.wrappers import handle_exception
from core.url.utils import build_url, build_url_with_query
from core.requests.utils import send_request
from movies.models import Movie, Cast, Crew
from movies.languages.constants import LANGUAGES

env = Env()

class MovieMetadata:
    class TMDB:
        def __init__(self):
            self.api_url = "https://api.themoviedb.org/3/"
            self.token = env.str("TMDB_TOKEN", "")
            self.latest_movie_id = self._fetch_latest_movie_id()

        @handle_exception
        def _fetch_latest_movie_id(self):
            url = build_url(self.api_url, "movie/latest")
            headers = {
                "Authorization": f"Bearer {self.token}",
            }
            response = send_request(
                method=HTTPMethod.GET.value,
                url= url,
                headers=headers,
            )
            response_body = response.json()
            return response_body["id"]

        @handle_exception
        def fetch_details(self, movie_id):
            url = build_url(self.api_url, "movie", movie_id)
            query = {
                "append_to_response": (
                    "credits,images,keywords,recommendations,similar"
                ),
                "language": "en-US",
                "include_image_language": "en,null"
            }
            url_with_query = build_url_with_query(url, query)
            headers = {
                "User-Agent": USER_AGENT,
                "Authorization": f"Bearer {self.token}",
            }
            response = send_request(
                method=HTTPMethod.GET.value,
                url=url_with_query,
                headers=headers,
            )
            response_body = response.json()
            return response_body

        @handle_exception
        def fetch_changed_movie_ids(self):
            movie_ids = []
            page = 1
            total_pages = 1
            url = build_url(self.api_url, "movie/changes")
            headers = {
                "User-Agent": USER_AGENT,
                "Authorization": f"Bearer {self.token}",
            }
            while page <= total_pages:
                payload = {
                    "page": page,
                    "limit": self.PAGINATION_LIMIT
                }
                response =  send_request(
                    method=HTTPMethod.GET.value,
                    url=url,
                    payload=payload,
                    headers=headers,
                )
                response_body = response.json()
                total_pages = response_body["total_pages"]
                for result in response_body["results"]:
                    if result["adult"]:
                        continue
                    movie_ids.append(result["id"])
                page += 1
            return movie_ids

        @handle_exception
        # TODO: Perhaps separate responsibilites. Use this only to fetch movie changes and do updating in management task
        def fetch_movie_changes_and_update(self, movie_id):
            movie = Movie.objects.get(id=movie_id)
            page = 1
            url = build_url(self.api_url, "movie", movie_id, "changes")
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
            array_fields = {
                field_map["spoken_languages"]: field_map["spoken_languages"],
                field_map["images"]: field_map["images"],
                field_map["plot_keywords"]: field_map["plot_keywords"],
            }
            association_fields = {
                field_map["genres"]: field_map["genres"],
                field_map["cast"]: field_map["cast"],
                field_map["crew"]: field_map["crew"],
            }
            image_types = {
                "poster": "poster",
                "backdrop": "backdrop",
                "logo": "logo",
                "title_logo": "title_logo",
            }
            actions = {
                "added": "added",
                "updated": "updated",
                "deleted": "deleted",
            }
            headers = {
                "User-Agent": USER_AGENT,
                "Authorization": f"Bearer {self.token}",
            }
            payload = { "page": page }
            response =  send_request(
                method=HTTPMethod.GET.value,
                url=url,
                payload=payload,
                headers=headers,
            )
            response_body =  response.json()
            for change in response_body["changes"]:
                key = change["key"]
                if key not in field_map.keys():
                    continue

                if key == field_map["images"]:
                    image_type = list(value.keys())[0]

                    if image_type == image_types["poster"]:
                        field = movie.posters
                    elif image_type == image_types["backdrop"]:
                        field = movie.backdrops
                    elif image_type == image_types["logo"] or image_type == image_types["title_logo"]:
                        field = movie.logos
                    else:
                        raise ValueError("Unknown image type")
                else:
                    field = getattr(movie, field_map[key])
                
                if type(field) == list:
                    field = map(ast.literal_eval, field)

                for item in change["items"]:
                    action = item["action"]
                    value = item["value"]

                    if key == field_map["genres"]:
                        if action == actions["added"]:
                            movie.genres.add(value["id"])
                        elif action == actions["deleted"]:
                            movie.genres.remove(value["id"])
                        else:
                            raise Exception(f"Unknown action while updating movie's genres: {action}.")
                    elif key == field_map["cast"]:
                        if action == actions["added"]:
                            Cast.objects.create(
                                credit_id=value["credit_id"],
                                character=value["character"],
                                movie=movie,
                                person_id=value["id"],
                            )
                        elif action == actions["deleted"]:
                            Cast.objects.filter(credit_id=value["credit_id"]).delete()
                        else:
                            raise Exception(f"Unknown action while updating movie's cast: {action}.")
                        field = movie.cast_set
                    elif key == field_map["crew"]:
                        if action == actions["added"]:
                            Cast.objects.create(
                                credit_id=value["credit_id"],
                                department=value["department"],
                                job=value["job"],
                                movie=movie,
                                person_id=value["id"],
                            )
                        elif action == actions["deleted"]:
                            Crew.objects.filter(credit_id=value["credit_id"]).delete()
                        else:
                            raise Exception(f"Unknown action while updating movie's crew: {action}.")
                    elif key == field_map["images"]:
                        if action == actions["added"]:
                            field.append(value)
                        elif action == actions["updated"]:
                            original_value = item["original_value"]
                            file_path = original_value[image_type]["file_path"]
                            image = next(x for x in field if x["file_path"] == file_path)

                            for k, v in value[image_type].items():
                                image[k] = v
                        elif action == actions["deleted"]:
                            field = [x for x in field if x != value]
                        else:
                            raise ValueError(f"Unknown action while updating movie's {image_type}: {action}")
                    elif key == field_map["spoken_languages"]:
                        if len(change["items"]) > 1:
                            raise ValueError("There should only be one item when updating movie's spoken languages.")

                        if action == actions["added"]:
                            for iso_639_1 in value:
                                field.append(LANGUAGES[iso_639_1])
                        elif action == actions["updated"]:
                            field = []
                            for iso_639_1 in value:
                                field.append(LANGUAGES[iso_639_1])
                        elif action == actions["deleted"]:
                            for iso_639_1 in value:
                                field = [x for x in field if x != LANGUAGES[iso_639_1]]
                        else:
                            raise Exception(f"Unknown action while updating movie's spoken languages: {action}")
                    elif key == field_map["plot_keywords"]:
                        if action == actions["added"]:
                            field.append(value)
                        elif action == actions["deleted"]:
                            field = [x for x in field if x != value]
                        else:
                            raise Exception(f"Unknown action while updating movie's keywords: {action}")
                    else:
                        if action == actions["updated"]:
                            field = value
                        elif action == actions["deleted"]:
                            field = None
                        else:
                            raise ValueError(f"Unknown action while updating movie's {field_map[key]}: {action}")
                movie.save()
