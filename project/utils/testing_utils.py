from unittest.mock import Mock, patch
from http import HTTPStatus


def _mock_response(response):
    mock_response = Mock()
    if response.get("status_code"):
        mock_response.status_code = response["status_code"]
    else:
        mock_response.status_code = HTTPStatus.OK.value
    mock_response.json.return_value = response["body"]
    return mock_response


def stub_request(instance, *, response):
    return patch(
        f"{instance.__class__.__module__}.send_request",
        return_value=_mock_response(response),
    )


def stub_multiple_requests(instance, *, responses: list):
    return patch(
        f"{instance.__class__.__module__}.send_request",
        side_effect=map(_mock_response, responses)
    )
