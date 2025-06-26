from http import HTTPMethod

from requests import get, post

from core.wrappers import handle_exception
from core.environments.utils import is_test
from project.settings import SKIP_EXTERNAL_TESTS


@handle_exception
def send_request(*, method, url, headers={}, payload={}):
    if is_test() and SKIP_EXTERNAL_TESTS.value:
        raise RuntimeError("""
        Attempted to send a real request in test environment.
        Stub it or disable SKIP_EXTERNAL_TESTS.
        """
        )
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
