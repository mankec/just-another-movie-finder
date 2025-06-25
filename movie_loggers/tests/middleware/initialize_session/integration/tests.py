from django.test import TestCase, Client

from core.sessions.utils import initialize_session
from core.sessions.constants import DEFAULT_SESSION_DATA
from movie_loggers.tests.services.constants import DEFAULT_TEST_MOVIE_LOGGER


class InitializeSessionMiddlewareIntegrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_initializes_session(self):
        self.assertFalse(self.client.session.items())
        self.client.get("/")
        self.assertTrue(
            dict(self.client.session.items()),
            DEFAULT_SESSION_DATA
        )

    def test_does_not_override_existing_values(self):
        session = self.client.session
        initialize_session(session)
        session["movie_logger"] = DEFAULT_TEST_MOVIE_LOGGER
        session.save()
        self.client.get("/")
        self.assertEqual(
            self.client.session["movie_logger"],
            DEFAULT_TEST_MOVIE_LOGGER
        )

    def test_raise_if_session_keys_are_not_the_same_as_in_default_session_data(self):
        session = self.client.session
        session["movie_logger"] = DEFAULT_TEST_MOVIE_LOGGER
        session.save()
        message = "Session keys are not the same as in DEFAULT_SESSION_DATA."
        with self.assertRaisesMessage(ValueError, message):
            self.client.get("/")
