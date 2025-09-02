from django.urls import path

from project.settings import IS_TEST
from . import views

app_name = "oauth"
urlpatterns = [
    path("", views.index, name="index"),
    path("<str:movie_logger>/authorize-application",
        views.authorize_application,
        name="authorize_application",
    ),
]

if IS_TEST:
    urlpatterns += [
        path("<str:movie_logger>/selenium-sign-in",
            views.selenium_sign_in,
            name="selenium_sign_in"
        )
    ]
