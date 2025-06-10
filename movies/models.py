from django.db import models

class Movie(models.Model):
    class Meta:
        db_table = "movie"
        
    title = models.CharField(max_length=50, null=False, blank=True)
    slug = models.CharField(max_length=50, null=False, blank=True)
    image = models.ImageField(upload_to='movie_posters/', null=False, blank=True)
    runtime = models.PositiveIntegerField(null=False)
    status = models.CharField(max_length=20, null=False, blank=True)
    keep_updated = models.BooleanField(null=False, blank=True)
    year = models.PositiveSmallIntegerField(null=False,)
    tvdb_id = models.PositiveIntegerField(null=False)
    imdb_id = models.CharField(max_length=16, null=False, blank=True)
    tmdb_id = models.PositiveIntegerField(null=False)
    budget = models.PositiveIntegerField(null=False)
    box_office = models.PositiveIntegerField(null=False)
    country = models.CharField(max_length=60, null=False, blank=True)
    language = models.CharField(max_length=20, null=False, blank=True)
