from http import HTTPMethod

from requests import get, post

from core.wrappers import handle_exception


@handle_exception
def send_request(*, method, url, headers={}, payload={}):
    response = None
    match method:
        case HTTPMethod.GET.value:
            response = get(url, params=payload, headers=headers)
        case HTTPMethod.POST.value:
            response = post(url, json=payload, headers=headers)
        case _:
            raise ValueError(
                f"HTTP method '{method}' is not supported."
            )
    response.raise_for_status()
    return response
