import inspect
from unittest.mock import Mock, patch
from http import HTTPStatus
from enum import Enum

from selenium.webdriver.chrome.options import Options

def mock_response(response):
    if not isinstance(response, dict):
        # Response can be an exception
        return response
    mock_response = Mock()
    if status_code := response.get("status_code"):
        mock_response.status_code = status_code
    else:
        mock_response.status_code = HTTPStatus.OK.value
    if headers := response.get("headers"):
        mock_response.headers = headers
    mock_response.json.return_value = response["body"]
    return mock_response


def stub_request(klass_or_instance, *, response):
    if inspect.isclass(klass_or_instance):
        klass = klass_or_instance
    else:
        klass = klass_or_instance.__class__
    return patch(
        f"{klass.__module__}.send_request",
        return_value=mock_response(response),
    )


def stub_multiple_requests(klass_or_instance, *, responses: list):
    if inspect.isclass(klass_or_instance):
        klass = klass_or_instance
    else:
        klass = klass_or_instance.__class__
    return patch(
        f"{klass.__module__}.send_request",
        side_effect=map(mock_response, responses)
    )


def stub_request_exception(klass_or_instance, *, exception):
    if inspect.isclass(klass_or_instance):
        klass = klass_or_instance
    else:
        klass = klass_or_instance.__class__
    return patch(
        f"{klass.__module__}.send_request",
        side_effect=exception,
    )


class ChromeMode(Enum):
    HEADLESS = "headless"
    DEFAULT = "default"

    @property
    def options(self):
        options = Options()
        if self.value == "headless":
            options.add_argument("--headless")
        return options

    @property
    def reason(self):
        return """
        Chrome Headless mode should only be disabled when testing locally. If you wish to ignore this check append `--exclude-tag=ci`. Refer to https://docs.djangoproject.com/en/5.2/topics/testing/tools/#tagging-tests.
        """
