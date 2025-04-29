from unittest.mock import patch


def stub_request(instance, *, return_value):
    return patch(
        f"{instance.__class__.__module__}.send_request",
        return_value=return_value
    )
