from http import HTTPStatus

from django.test import TestCase, Client
from django.http import HttpResponse

from project.settings import PRODUCTION_HOST, PRODUCTION_HOST_WITH_SUBDOMAIN, PRODUCTION_URL
from core.middleware.redirect_www.middleware import RedirectWwwMiddleware

class RedirectWwwMiddlewareIntegrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_redirect_for_www_host(self):
        response = self.client.get("/", HTTP_HOST=PRODUCTION_HOST_WITH_SUBDOMAIN, follow=True)
        self.assertRedirects(
            response,
            PRODUCTION_URL,
            status_code=HTTPStatus.MOVED_PERMANENTLY.value
        )

    def test_no_redirect_for_non_www_host(self):
        response = self.client.get("/", HTTP_HOST=PRODUCTION_HOST)
        self.assertEqual(response.status_code, 200)
