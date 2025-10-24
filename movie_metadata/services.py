from http import HTTPMethod, HTTPStatus

from environs import Env
from requests.exceptions import HTTPError

from project.settings import USER_AGENT
from core.wrappers import handle_exception
from core.url.utils import build_url, build_url_with_query
from core.requests.utils import send_request

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
