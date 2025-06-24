from unittest import TestCase

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from django.http import HttpResponse
from django.contrib.messages import get_messages


class CustomAssertionsMixin:
    def assertFlashMessage(self: TestCase, response: HttpResponse, expected_message: str):
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(messages, "No flash messages found in response.")
        self.assertEqual(len(messages), 1, "Multiple flash messages found in response.")
        message = messages[0].message
        self.assertEqual(message, expected_message)

    def assertJsFlashMessage(self, expected_message: str, timeout=5):
        flash_message = WebDriverWait(self.selenium, timeout).until(
            expected_conditions.visibility_of_element_located(
                (By.ID, "flash-message-text")
            )
        )
        self.assertEqual(expected_message, flash_message.text)
