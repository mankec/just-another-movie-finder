from unittest.mock import Mock, patch
from http import HTTPStatus


def mock_response(response):
    mock_response = Mock()
    if status_code := response.get("status_code"):
        mock_response.status_code = status_code
    else:
        mock_response.status_code = HTTPStatus.OK.value
    if headers := response.get("headers"):
        mock_response.headers = headers
    mock_response.json.return_value = response["body"]
    return mock_response


def stub_request(instance, *, response):
    return patch(
        f"{instance.__class__.__module__}.send_request",
        return_value=mock_response(response),
    )


def stub_multiple_requests(instance, *, responses: list):
    return patch(
        f"{instance.__class__.__module__}.send_request",
        side_effect=map(mock_response, responses)
    )


def stub_request_exception(instance, *, exception):
    return patch(
        f"{instance.__class__.__module__}.send_request",
        side_effect=exception,
    )
