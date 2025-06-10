from django.db import models

class Movie(models.Model):
    class Meta:
        db_table = "movie"
        
    title = models.CharField(max_length=50, null=False, blank=True)
    slug = models.CharField(max_length=50, null=False, blank=True)
    last_updated = models.CharField(
        null=False,
        blank=True,
        db_comment="Date and time when the movie was last updated from TVDB.",
    )
    image = models.ImageField(upload_to='movie_posters/', null=False, blank=True)
    runtime = models.PositiveIntegerField(null=False)
    status = models.CharField(max_length=20, null=False, blank=True)
    keep_updated = models.BooleanField(null=False, blank=True)
    year = models.PositiveSmallIntegerField(null=False, blank=True)
    tvdb_id = models.PositiveIntegerField(null=False)
    imdb_id = models.CharField(max_length=16, null=True)
    tmdb_id = models.PositiveIntegerField(null=True)
    budget = models.PositiveIntegerField(null=True)
    box_office = models.PositiveIntegerField(null=True)
    country = models.CharField(max_length=60, null=False, blank=True)
    language = models.CharField(max_length=20, null=False, blank=True)
