from unittest.mock import patch

def stub_request(instance, *, response):
    return patch(
        f"{instance.__class__.__module__}.send_request",
        return_value=response,
    )

def stub_multiple_requests(instance, *, responses: list):
    return patch(
        f"{instance.__class__.__module__}.send_request",
        side_effect=responses
    )
