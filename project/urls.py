from django.contrib import admin
from django.urls import include, path

from movies import views as movies_views
from auth import views as auth_views

urlpatterns = [
    path("", movies_views.index, name="index"), # Root
    path("sign-in", auth_views.sign_in, name="sign_in"),
    path("sign-out", auth_views.sign_out, name="sign_out"),
    # TODO: Put this in core app
    path('error/', movies_views.error, name='error'),
    path("movies/", include("movies.urls")),
    path("auth/", include("auth.urls")),
    # path("admin/", admin.site.urls),
]
