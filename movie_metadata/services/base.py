from http import HTTPMethod, HTTPStatus

from environs import Env

from project.utils.url_utils import build_url
from project.utils.request_utils import send_request, build_url

env = Env()

class MovieMetadata:
    class TVDB:
        def __init__(self):
            self.api_url = "https://api4.thetvdb.com/v4/"
            self.api_key = env.str("TVDB_API_KEY", "")
            self.token = env.str("TVDB_TOKEN", "") or self._fetch_token()
            self.total_movies = self._fetch_total_movies()

        def _fetch_token(self):
            try:
                url = build_url(self.api_url, "login")
                payload = {
                    "apikey": self.api_key,
                }
                response = send_request(
                    method=HTTPMethod.POST.name,
                    url= url,
                    payload=payload,
                )
                response_body = response.json()
                # Save token in .envrc
                # print(response_body["data"]["token"])
            except Exception as error:
                # TODO: Create logger for messages like these
                # It should show file path where error happend and it should display error message
                print("Failed to fetch token from TVDB: %s" % error)

        def _fetch_total_movies(self):
            try:
                url = build_url(self.api_url, "movies")
                headers = {
                    "Authorization": f"Bearer {self.token}",
                }
                response = send_request(
                    method=HTTPMethod.GET.name,
                    url= url,
                    headers=headers,
                )
                return response["links"]["total_items"]
            except Exception as error:
                print("Failed to fetch total movies from TVDB: %s" % error)

        def fetch_extended(self, movie_id):
            url = build_url(self.api_url, "movies", movie_id, "extended")
            headers = {
                "Authorization": f"Bearer {self.token}",
            }
            try:
                response = send_request(
                    method=HTTPMethod.GET.name,
                    url=url,
                    headers=headers,
                )
                if response.status_code == HTTPStatus.NOT_FOUND.value:
                    raise Exception(HTTPStatus.NOT_FOUND.phrase)
                response_body = response.json()
                return response_body
            except Exception as error:
                print("Failed to fetch movie from TVDB: %s" % error)
                raise
