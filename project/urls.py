from django.contrib import admin
from django.urls import include, path

from movies import views as movies_views

urlpatterns = [
    path("", movies_views.index, name="index"), # Root
    path("sign-in", movies_views.sign_in, name="sign_in"),
    path("sign-out", movies_views.sign_out, name="sign_out"),
    path("movies/", include("movies.urls")),
    # path("admin/", admin.site.urls),
]
