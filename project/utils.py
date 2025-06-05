import re
from urllib.parse import urlencode

from requests import get, post, RequestException

def build_url(*path_segments):
    return "/".join(str(path_segment).strip("/") for path_segment in path_segments)


def build_url_with_query(url, query):
    return f"{url}?{urlencode(query)}"


def send_request(*, method, url, headers={}, payload={}):
    try:
        match method:
            case "GET":
                response = get(url, params=payload, headers=headers)
            case "POST":
                response = post(url, json=payload, headers=headers)
            case _:
                raise ValueError(
                    f"Hey it's {method} method and I am not supported!" \
                    "Please update me at movies/services/apis/loggers/helpers.py."
                )
        response.raise_for_status()

        return response.json()
    except RequestException:
        raise


def hyphenate(text):
    return re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-")
