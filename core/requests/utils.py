import traceback
from traceback import FrameSummary
from http import HTTPMethod

from requests import get, post

from core.wrappers import handle_exception
from core.environments.utils import is_test


@handle_exception
def send_request(*, method, url, headers={}, payload={}):
    if is_test():
        stack = traceback.extract_stack()
        fs: FrameSummary = stack[-3]
        raise RuntimeError(f"""
        Attempted to send a real request in test environment.
        {fs.filename}
        Called by `{fs.name}`.
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
