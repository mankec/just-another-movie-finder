from django.contrib import admin
from django.urls import include, path

from movies import views as movies_views

app_name = "movies"
urlpatterns = [
    path("", movies_views.index, name="index"), # Root
    path("movies/", include("movies.urls")),
    # path("admin/", admin.site.urls),
]
