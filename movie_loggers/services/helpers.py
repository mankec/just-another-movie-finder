from requests import get, post, RequestException
from movies.utils import hyphenate


def send_request(*, method, url, headers={}, payload={}):
    try:
        match method:
            case "GET":
                response = get(url, params=payload)
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


def tvdb_id(id, title):
    return f"{id}, {hyphenate(title).lower()}"
