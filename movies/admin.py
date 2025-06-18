from django.contrib import admin
from movies.models import Movie, Genre


class MovieAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    filter_horizontal = ('genres',)


admin.site.register(Movie, MovieAdmin)
admin.site.register(Genre)
