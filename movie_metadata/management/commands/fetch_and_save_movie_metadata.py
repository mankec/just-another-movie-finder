from django.core.management.base import BaseCommand, CommandError
from movie_metadata.services.base import MovieMetadata

class Command(BaseCommand):
    help = "Fetch and save movie metadata from TVDB."

    def handle(self, *args, **options):
        response = MovieMetadata.TVDB().fetch_all()
        next_page_url = response["links"]["next"]
        self._create_movies(response["data"])

        while next_page_url:
            print(next_page_url)
            response = MovieMetadata.TVDB().fetch_all(next_page_url)
            next_page_url = response["links"]["next"]
            self._create_movies(response["data"])

    def _create_movies(self, data):
        ...
