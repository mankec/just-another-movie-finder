from django.contrib import admin
from django.urls import include, path

from app import views as app_views

urlpatterns = [
    path("", app_views.index, name="index"), # Root
    path("app/", include("app.urls")),
    path("admin/", admin.site.urls),
]
