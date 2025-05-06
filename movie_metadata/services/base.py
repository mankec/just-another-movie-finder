from urllib.parse import urljoin

from environs import Env

from project.utils import send_request

env = Env()

class MovieMetadata:
    class TVDB:
        def __init__(self):
            self.api_url = "https://api4.thetvdb.com/v4/"
            self.api_key = env.str("TVDB_API_KEY")
            self.token = env.str("TVDB_TOKEN", "") or self._fetch_token()

        def _fetch_token(self):
            url = urljoin(self.api_url, "login")
            payload = {
                "apikey": self.api_key,
            }
            response = send_request(
                method="POST",
                url= url,
                payload=payload,
            )
            # Save token in .envrc
            # print(response["data"]["token"])

        def fetch_all(self, next_page_url=""):
            url = next_page_url or urljoin(self.api_url, "movies")
            headers = {
                "Authorization": f"Bearer {self.token}",
            }
            response = send_request(
                method="GET",
                url=url,
                headers=headers,
            )
            return response
