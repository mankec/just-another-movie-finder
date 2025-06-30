from http import HTTPMethod, HTTPStatus

from environs import Env
from requests.exceptions import HTTPError

from core.wrappers import handle_exception
from core.url.utils import build_url
from core.requests.utils import send_request

env = Env()

class MovieMetadata:
    class TVDB:
        def __init__(self):
            self.api_url = "https://api4.thetvdb.com/v4/"
            self.api_key = env.str("TVDB_API_KEY", "")
            self.token = env.str("TVDB_TOKEN", "") or self._fetch_token()
            self.total_movies = self._fetch_total_movies()

        @handle_exception
        def _fetch_token(self):
            url = build_url(self.api_url, "login")
            payload = {
                "apikey": self.api_key,
            }
            response = send_request(
                method=HTTPMethod.POST.value,
                url= url,
                payload=payload,
            )
            response_body = response.json()
            # Save token in .envrc
            # print(response_body["data"]["token"])

        @handle_exception
        def _fetch_total_movies(self):
            url = build_url(self.api_url, "movies")
            headers = {
                "Authorization": f"Bearer {self.token}",
            }
            response = send_request(
                method=HTTPMethod.GET.value,
                url= url,
                headers=headers,
            )
            response_body = response.json()
            return response_body["links"]["total_items"]

        @handle_exception
        def fetch_extended(self, movie_id):
            url = build_url(self.api_url, "movies", movie_id, "extended")
            headers = {
                "Authorization": f"Bearer {self.token}",
            }
            response = send_request(
                method=HTTPMethod.GET.value,
                url=url,
                headers=headers,
            )
            response_body = response.json()
            return response_body
