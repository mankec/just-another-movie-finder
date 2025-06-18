from django.contrib import admin
from django.urls import include, path

from movies import views as movies_views
from oauth import views as auth_views
from core import views as core_views

urlpatterns = [
    path("", movies_views.index, name="index"), # Root
    path("sign-in", auth_views.sign_in, name="sign_in"),
    path("sign-out", auth_views.sign_out, name="sign_out"),
    path('error/', core_views.error, name='error'),
    path("oauth/", include("oauth.urls")),
    path("movies/", include("movies.urls")),
    # path("admin/", admin.site.urls),
]
