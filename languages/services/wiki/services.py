from http import HTTPMethod

from project.settings import USER_AGENT
from core.wrappers import handle_exception
from core.requests.utils import send_request


class Wiki:
    API_URL = "https://en.wikipedia.org/w/api.php"
    REQUIRED_HEADERS = {
        "User-Agent": USER_AGENT,
    }

    @classmethod
    @handle_exception
    def fetch_page_content(cls, *, page):
        payload = {
            "action": "parse",
            "page": page,
            "prop": "text",
            "format": "json"
        }
        response = send_request(
            method=HTTPMethod.GET.value,
            url=cls.API_URL,
            headers=cls.REQUIRED_HEADERS,
            payload=payload,
        )
        return response.content
