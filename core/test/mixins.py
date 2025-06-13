from unittest import TestCase

from django.http import HttpResponse
from django.contrib.messages import get_messages


class CustomAssertionsMixin:
    def assertFlashMessage(self: TestCase, response: HttpResponse, expected_message: str):
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(messages, "No flash messages found in response.")
        message = messages[0].message
        self.assertEqual(message, expected_message)
