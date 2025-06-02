from http import HTTPMethod

from requests import get, post, RequestException

# TODO: Add tests for this method
def send_request(*, method, url, headers={}, payload={}):
    response = None
    try:
        match method:
            case HTTPMethod.GET.name:
                response = get(url, params=payload, headers=headers)
            case HTTPMethod.POST.name:
                response = post(url, json=payload, headers=headers)
            case _:
                raise ValueError(
                    f"Hey it's {method} method and I am not supported!" \
                    "Please update me at movies/services/apis/loggers/helpers.py."
                )
        return response
    except RequestException as error:
        if response is not None:
            print("RequestException in send_request: %s" % error)
        else:
            print("Response doesn't exist: %s" % error)
            raise
    except Exception as error:
        print("Error while sending request: %s" % error)
        raise
