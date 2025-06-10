from django.db import models

class Movie(models.Model):
    class Meta:
        db_table = "movie"
        
    title = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255)
    last_updated = models.CharField(
        db_comment="Date and time when the movie was last updated from TVDB.",
    )
    image = models.ImageField(upload_to='movie_posters/', null=True)
    runtime = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, blank=True)
    keep_updated = models.BooleanField()
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    tvdb_id = models.PositiveIntegerField()
    imdb_id = models.CharField(max_length=16, null=True)
    tmdb_id = models.PositiveIntegerField(null=True)
    budget = models.PositiveBigIntegerField(null=True)
    box_office = models.PositiveBigIntegerField(null=True)
    country = models.CharField(max_length=60, blank=True)
    language = models.CharField(max_length=20, blank=True)
