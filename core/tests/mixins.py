from unittest import TestCase

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from django.http import HttpResponse
from django.contrib.messages import get_messages
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

from core.url.utils import build_url


class CustomAssertionsMixin:
    def assertFlashMessage(self: TestCase, response: HttpResponse, expected_message: str):
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(messages, "No flash messages found in response.")
        self.assertEqual(len(messages), 1, "Multiple flash messages found in response.")
        message = messages[0].message
        self.assertEqual(message, expected_message)

    def assertJsFlashMessage(self: TestCase, expected_message: str, timeout=5):
        flash_message = WebDriverWait(self.browser, timeout).until(
            expected_conditions.visibility_of_element_located(
                (By.ID, "flash-message-text")
            )
        )
        self.assertEqual(expected_message, flash_message.text)

    def refuteJsFlashMessage(self: TestCase):
        self.assertFalse(self.browser.find_elements(By.ID, "flash-message-text"))


class CustomSeleniumMixin:
    def selenium_sign_in_user(self: TestCase, movie_logger):
        try:
            url = reverse("oauth:selenium_sign_in", kwargs={
                "movie_logger": movie_logger,
            })
            self.browser.get(self.selenium_url(url))
        except NoReverseMatch:
            self.fail("This URL is only available in test environment. Run `DJANGO_ENV=test python manage.py test` to be able to access it.")

    def selenium_url(self: TestCase, url) -> str:
        return build_url(self.live_server_url, url)
