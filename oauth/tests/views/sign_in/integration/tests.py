from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from core.tests.mixins import CustomAssertionsMixin
from core.sessions.utils import initialize_session
from core.tests.utils import sign_in_user


class SignInViewIntegrationTestCase(TestCase, CustomAssertionsMixin):
    def test_user_is_redirected_from_sign_in_page_if_already_signed_in(self):
        client = Client()
        session = client.session
        initialize_session(session)
        session.save()
        url = reverse("sign_in")

        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

        sign_in_user(session)

        message = "Already signed in."
        expected_url = "/"
        response = client.get(url, follow=True)
        self.assertFlashMessage(response, message)
        self.assertRedirects(
                response,
                expected_url,
                fetch_redirect_response=False
            )
