import ast
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from core.tests.utils import stub_requests, mock_response
from core.constants import TMDB_ACTIONS
from movies.languages.constants import LANGUAGES
from movie_metadata.services import MovieMetadata
from movies.models import Movie, Genre, Person, Cast, Crew

class SyncMovieChangesTest(TestCase):
    fixtures = ["movies.json", "genres.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fetch_latest_movie_id_patcher = patch('movie_metadata.services.MovieMetadata.TMDB._fetch_latest_movie_id', return_value=2)
        cls.mock_fetch_latest_movie_id = cls.fetch_latest_movie_id_patcher.start()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.fetch_latest_movie_id_patcher.stop()

    def setUp(self):
        self.tmdb = MovieMetadata.TMDB()
        self.movie = Movie.objects.get(id=1)
        self.movie_changes_response = {
            "body": {
                "results": [
                    {
                        "id": self.movie.id,
                        "adult": False
                    }
                ],
                "page": 1,
                "total_pages": 1,
            }
        }
        self.cast_person_1 = Person.objects.create(
            name="Cast Name 1",
            original_name="Cast Name 1",
            id=1,
        )
        self.cast_person_2 = Person.objects.create(
            name="Cast Name 2",
            original_name="Cast Name 2",
            id=2,
        )
        self.crew_person_1 = Person.objects.create(
            name="Crew Name 1",
            original_name="Crew Name 1",
            id=3,
        )
        self.crew_person_2 = Person.objects.create(
            name="Crew Name 2",
            original_name="Crew Name 2",
            id=4,
        )
        self.cast_1 = Cast.objects.create(
            person_id=self.cast_person_1.id,
            credit_id="cast_credit_id_1",
            character="Character Name 1",
            movie=self.movie
        )
        self.cast_2 = Cast.objects.create(
            person_id=self.cast_person_2.id,
            credit_id="cast_credit_id_2",
            character="Character Name 2",
            movie=self.movie
        )
        self.crew_1 = Crew.objects.create(
            person_id=self.crew_person_1.id,
            job="Writer",
            department="Writing",
            credit_id="crew_credit_id_1",
            movie=self.movie
        )
        self.crew_2 = Crew.objects.create(
            person_id=self.crew_person_2.id,
            job="Writer",
            department="Writing",
            credit_id="crew_credit_id_2",
            movie=self.movie
        )
        self.genre_1 = Genre.objects.get(pk=27)
        self.genre_2 = Genre.objects.get(pk=28)
        self.new_poster_1_path = "/new_poster_1.jpg"
        self.new_poster_2_path = "/new_poster_2.jpg"
        self.poster_1_path = "/poster_1.jpg"
        self.poster_2_path = "/poster_2.jpg"

    def test_cast_added(self):
        new_cast_credit_id_1 = "new_cast_credit_id_1"
        new_cast_credit_id_2 = "new_cast_credit_id_2"
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "cast",
                            "items": [
                                {
                                    "id": "69151f822075737f024c9348",
                                    "action": TMDB_ACTIONS["added"],
                                    "time": "2025-11-13 00:00:02 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "value": {
                                        "person_id": self.cast_person_1.id,
                                        "character": "New Character 1",
                                        "credit_id": new_cast_credit_id_1
                                    }
                                },
                                {
                                    "id": "6915226eeacffe65b23a3e39",
                                    "action": TMDB_ACTIONS["added"],
                                    "time": "2025-11-13 00:12:30 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "value": {
                                        "person_id": self.cast_person_2.id,
                                        "character": "New Character 2",
                                        "credit_id": new_cast_credit_id_2
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.assertTrue(Cast.objects.filter(credit_id=new_cast_credit_id_1).exists())
            self.assertTrue(Cast.objects.filter(credit_id=new_cast_credit_id_2).exists())

    def test_cast_deleted(self):
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "cast",
                            "items": [
                                {
                                    "id": "69151f822075737f024c9348",
                                    "action": TMDB_ACTIONS["deleted"],
                                    "time": "2025-11-13 00:00:02 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "original_value": {
                                        "person_id": self.cast_person_1.id,
                                        "character": self.cast_1.character,
                                        "credit_id": self.cast_1.credit_id
                                    }
                                },
                                {
                                    "id": "6915226eeacffe65b23a3e39",
                                    "action": TMDB_ACTIONS["deleted"],
                                    "time": "2025-11-13 00:12:30 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "original_value": {
                                        "person_id": self.cast_person_2.id,
                                        "character": self.cast_2.character,
                                        "credit_id": self.cast_2.credit_id
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.assertFalse(Cast.objects.filter(credit_id=self.cast_1.credit_id).exists())
            self.assertFalse(Cast.objects.filter(credit_id=self.cast_2.credit_id).exists())

    def test_crew_added(self):
        new_crew_credit_id_1 = "new_crew_credit_id_1"
        new_crew_credit_id_2 = "new_crew_credit_id_2"
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "crew",
                            "items": [
                                {
                                    "id": "6915200cc48e7e4aa7ac21d4",
                                    "action": TMDB_ACTIONS["added"],
                                    "time": "2025-11-13 00:02:20 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "value": {
                                        "person_id": self.crew_person_1.id,
                                        "department": "Costume & Make-Up",
                                        "job": "Makeup Designer",
                                        "credit_id": new_crew_credit_id_1
                                    }
                                },
                                {
                                    "id": "6915200cc48e7e4aa7ac21d4",
                                    "action": TMDB_ACTIONS["added"],
                                    "time": "2025-11-13 00:02:20 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "value": {
                                        "person_id": self.crew_person_2.id,
                                        "department": "Costume & Make-Up",
                                        "job": "Makeup Designer",
                                        "credit_id": new_crew_credit_id_2
                                    }
                                },
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.assertTrue(Crew.objects.filter(credit_id=new_crew_credit_id_1).exists())
            self.assertTrue(Crew.objects.filter(credit_id=new_crew_credit_id_2).exists())

    def test_crew_deleted(self):
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "crew",
                            "items": [
                                {
                                    "id": "6915200cc48e7e4aa7ac21d4",
                                    "action": TMDB_ACTIONS["deleted"],
                                    "time": "2025-11-13 00:02:20 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "original_value": {
                                        "person_id": self.crew_person_1.id,
                                        "department":self.crew_1.department,
                                        "job": self.crew_1.job,
                                        "credit_id": self.crew_1.credit_id
                                    }
                                },
                                {
                                    "id": "6915200cc48e7e4aa7ac21d4",
                                    "action": TMDB_ACTIONS["deleted"],
                                    "time": "2025-11-13 00:02:20 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "original_value": {
                                        "person_id": self.crew_person_2.id,
                                        "department": self.crew_2.department,
                                        "job": self.crew_2.job,
                                        "credit_id": self.crew_2.credit_id
                                    }
                                },
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.assertFalse(Crew.objects.filter(credit_id=self.crew_1.credit_id).exists())
            self.assertFalse(Crew.objects.filter(credit_id=self.crew_2.credit_id).exists())

    def test_genres_added(self):
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "genres",
                            "items": [
                                {
                                    "id": "691520e8535cb85e69ac20e3",
                                    "action": TMDB_ACTIONS["added"],
                                    "time": "2025-11-13 00:06:00 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "value": {
                                        "name": self.genre_1.name,
                                        "id": self.genre_1.id
                                    }
                                },
                                {
                                    "id": "691520ed2f9649b50a4c960a",
                                    "action": TMDB_ACTIONS["added"],
                                    "time": "2025-11-13 00:06:05 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "value": {
                                        "name": self.genre_1.name,
                                        "id": self.genre_2.id
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.movie.refresh_from_db()
            genre_names = list(self.movie.genres.all().order_by("id").values_list("name", flat=True))
            expected = [self.genre_1.name, self.genre_2.name]
            self.assertEqual(genre_names, expected)

    def test_genres_deleted(self):
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "genres",
                            "items": [
                                {
                                    "id": "691520e8535cb85e69ac20e3",
                                    "action": TMDB_ACTIONS["deleted"],
                                    "time": "2025-11-13 00:06:00 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "original_value": {
                                        "name": self.genre_1.name,
                                        "id": self.genre_1.id
                                    }
                                },
                                {
                                    "id": "691520ed2f9649b50a4c960a",
                                    "action": TMDB_ACTIONS["deleted"],
                                    "time": "2025-11-13 00:06:05 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "original_value": {
                                        "name": self.genre_1.name,
                                        "id": self.genre_2.id
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.movie.refresh_from_db()
            genre_names = list(self.movie.genres.all().order_by("id").values_list("name", flat=True))
            expected = []
            self.assertEqual(genre_names, expected)

    def test_poster_images_added(self):
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "images",
                            "items": [
                                {
                                    "id": "6915249feba221c4a93a3f0c",
                                    "action": TMDB_ACTIONS["added"],
                                    "time": "2025-11-13 00:21:51 UTC",
                                    "iso_639_1": "es",
                                    "iso_3166_1": "MX",
                                    "value": {
                                        "poster": {
                                        "file_path": self.new_poster_1_path,
                                        "iso_639_1": "es",
                                        "iso_3166_1": "MX"
                                        }
                                    },
                                },
                                {
                                    "id": "691524a66e28e62421876478",
                                    "action": TMDB_ACTIONS["added"],
                                    "time": "2025-11-13 00:21:58 UTC",
                                    "iso_639_1": "es",
                                    "iso_3166_1": "MX",
                                    "value": {
                                        "poster": {
                                        "file_path": self.new_poster_2_path,
                                        "iso_639_1": "es",
                                        "iso_3166_1": "MX"
                                        }
                                    },
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.movie.refresh_from_db()
            posters = list(map(ast.literal_eval, self.movie.posters))
            expected = [self.poster_1_path, self.poster_2_path, self.new_poster_1_path,self. new_poster_2_path]
            poster_paths = [x["file_path"] for x in posters]
            self.assertEqual(poster_paths, expected)

    def test_poster_images_updated(self):
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "images",
                            "items": [
                                {
                                    "id": "6915249feba221c4a93a3f0c",
                                    "action": TMDB_ACTIONS["updated"],
                                    "time": "2025-11-13 00:21:51 UTC",
                                    "iso_639_1": "es",
                                    "iso_3166_1": "MX",
                                    "value": {
                                        "poster": {
                                        "file_path": self.new_poster_1_path,
                                        "iso_639_1": "es",
                                        "iso_3166_1": "MX"
                                        }
                                    },
                                    "original_value": {
                                        "poster": {
                                        "file_path": self.poster_1_path,
                                        "iso_639_1": "es",
                                        "iso_3166_1": "ES"
                                        }
                                    }
                                },
                                {
                                    "id": "691524a66e28e62421876478",
                                    "action": TMDB_ACTIONS["updated"],
                                    "time": "2025-11-13 00:21:58 UTC",
                                    "iso_639_1": "es",
                                    "iso_3166_1": "MX",
                                    "value": {
                                        "poster": {
                                        "file_path": self.new_poster_2_path,
                                        "iso_639_1": "es",
                                        "iso_3166_1": "MX"
                                        }
                                    },
                                    "original_value": {
                                        "poster": {
                                        "file_path": self.poster_2_path,
                                        "iso_639_1": "es",
                                        "iso_3166_1": "ES"
                                        }
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.movie.refresh_from_db()
            posters = list(map(ast.literal_eval, self.movie.posters))
            expected = [self.new_poster_1_path, self.new_poster_2_path]
            poster_paths = [x["file_path"] for x in posters]
            self.assertEqual(poster_paths, expected)

    def test_poster_images_deleted(self):
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "images",
                            "items": [
                                {
                                    "id": "6915249feba221c4a93a3f0c",
                                    "action": TMDB_ACTIONS["deleted"],
                                    "time": "2025-11-13 00:21:51 UTC",
                                    "iso_639_1": "es",
                                    "iso_3166_1": "MX",
                                    "original_value": {
                                        "poster": {
                                        "file_path": self.poster_1_path,
                                        "iso_639_1": "es",
                                        "iso_3166_1": "MX"
                                        }
                                    },
                                },
                                {
                                    "id": "691524a66e28e62421876478",
                                    "action": TMDB_ACTIONS["deleted"],
                                    "time": "2025-11-13 00:21:58 UTC",
                                    "iso_639_1": "es",
                                    "iso_3166_1": "MX",
                                    "original_value": {
                                        "poster": {
                                        "file_path": self.poster_2_path,
                                        "iso_639_1": "es",
                                        "iso_3166_1": "MX"
                                        }
                                    },
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.movie.refresh_from_db()
            posters = list(map(ast.literal_eval, self.movie.posters))
            expected = []
            poster_paths = [x["file_path"] for x in posters]
            self.assertEqual(poster_paths, expected)

    def test_spoken_languages_added(self):
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "spoken_languages",
                            "items": [
                                {
                                    "id": "6913af3e9913d3c4f9876a7d",
                                    "action": TMDB_ACTIONS["added"],
                                    "time": "2025-11-11 21:48:46 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "value": [
                                        "da",
                                        "fr"
                                    ],
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.movie.refresh_from_db()
            spoken_languages = list(map(ast.literal_eval, self.movie.spoken_languages))
            expected = [
                {
                    'english_name': LANGUAGES["da"]["english_name"],
                    'iso_639_1': 'da',
                    'name': LANGUAGES["da"]["name"]
                },
                {
                    'english_name': LANGUAGES["fr"]["english_name"],
                    'iso_639_1': 'fr',
                    'name': LANGUAGES["fr"]["name"]
                },
            ]
            self.assertEqual(spoken_languages, expected)

    def test_spoken_languages_updated(self):
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "spoken_languages",
                            "items": [
                                {
                                    "id": "6913af3e9913d3c4f9876a7d",
                                    "action": TMDB_ACTIONS["updated"],
                                    "time": "2025-11-11 21:48:46 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "value": [
                                        "da",
                                        "fr",
                                        "en"
                                    ],
                                    "original_value": [
                                        "da",
                                        "en",
                                        "fr"
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.movie.refresh_from_db()
            spoken_languages = list(map(ast.literal_eval, self.movie.spoken_languages))
            expected = [
                {
                    'english_name': LANGUAGES["da"]["english_name"],
                    'iso_639_1': 'da',
                    'name': LANGUAGES["da"]["name"]
                },
                {
                    'english_name': LANGUAGES["fr"]["english_name"],
                    'iso_639_1': 'fr',
                    'name': LANGUAGES["fr"]["name"]
                },
                {
                    'english_name': LANGUAGES["en"]["english_name"],
                    'iso_639_1': 'en',
                    'name': LANGUAGES["en"]["name"]
                },
            ]
            self.assertEqual(spoken_languages, expected)

    def test_spoken_languages_deleted(self):
        languages = [
                {
                    'english_name': LANGUAGES["da"]["english_name"],
                    'iso_639_1': 'da',
                    'name': LANGUAGES["da"]["name"]
                },
                {
                    'english_name': LANGUAGES["fr"]["english_name"],
                    'iso_639_1': 'fr',
                    'name': LANGUAGES["fr"]["name"]
                },
                {
                    'english_name': LANGUAGES["en"]["english_name"],
                    'iso_639_1': 'en',
                    'name': LANGUAGES["en"]["name"]
                },
        ]
        languages = [str(x) for x in languages]
        self.movie.spoken_languages = languages
        self.movie.save()
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "spoken_languages",
                            "items": [
                                {
                                    "id": "6913af3e9913d3c4f9876a7d",
                                    "action": TMDB_ACTIONS["deleted"],
                                    "time": "2025-11-11 21:48:46 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "original_value": [
                                        "da",
                                        "fr"
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.movie.refresh_from_db()
            spoken_languages = list(map(ast.literal_eval, self.movie.spoken_languages))
            expected = [
                {
                    'english_name': LANGUAGES["en"]["english_name"],
                    'iso_639_1': 'en',
                    'name': LANGUAGES["en"]["name"]
                },
            ]
            self.assertEqual(spoken_languages, expected)

    def test_keywords_added(self):
        keyword_1_id = 1
        keyword_2_id = 2
        keyword_1_name = "keyword_1"
        keyword_2_name = "keyword_2"
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "plot_keywords",
                            "items": [
                                {
                                    "id": "6923a0157398caa33c1872ba",
                                    "action": TMDB_ACTIONS["added"],
                                    "time": "2025-11-24 00:00:21 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "value": {
                                        "name": keyword_1_name,
                                        "id": keyword_1_id
                                    }
                                },
                                {
                                    "id": "6923a0157398caa33c1872ba",
                                    "action": TMDB_ACTIONS["added"],
                                    "time": "2025-11-24 00:00:21 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "value": {
                                        "name": keyword_2_name,
                                        "id": keyword_2_id
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.movie.refresh_from_db()
            keywords = list(map(ast.literal_eval, self.movie.keywords))
            expected = [
                {
                    "id": keyword_1_id,
                    "name": keyword_1_name
                },
                {
                    "id": keyword_2_id,
                    "name": keyword_2_name
                },
            ]
            self.assertEqual(keywords, expected)

    def test_keywords_deleted(self):
        keyword_1_id = 1
        keyword_2_id = 2
        keyword_1_name = "keyword_1"
        keyword_2_name = "keyword_2"
        keywords = [
                {
                    "id": keyword_1_id,
                    "name": keyword_1_name
                },
                {
                    "id": keyword_2_id,
                    "name": keyword_2_name
                },
        ]
        self.movie.keywords = keywords
        self.movie.save()
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "plot_keywords",
                            "items": [
                                {
                                    "id": "6923a0157398caa33c1872ba",
                                    "action": TMDB_ACTIONS["deleted"],
                                    "time": "2025-11-24 00:00:21 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "original_value": {
                                        "name": keyword_1_name,
                                        "id": keyword_1_id
                                    }
                                },
                                {
                                    "id": "6923a0157398caa33c1872ba",
                                    "action": TMDB_ACTIONS["deleted"],
                                    "time": "2025-11-24 00:00:21 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "original_value": {
                                        "name": keyword_2_name,
                                        "id": keyword_2_id
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.movie.refresh_from_db()
            keywords = list(map(ast.literal_eval, self.movie.keywords))
            expected = []
            self.assertEqual(keywords, expected)

    def test_updated_character_names(self):
        new_character_name_1 = "New Character Name 1"
        new_character_name_2 = "New Character Name 2"
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "character_names",
                            "items": [
                                {
                                    "id": "69151f818c84b2cc9c3a3d05",
                                    "action": TMDB_ACTIONS["updated"],
                                    "time": "2025-11-13 00:00:01 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "value": {
                                        "person_id": self.cast_1.person.id,
                                        "character": new_character_name_1,
                                        "cast_id": self.cast_1.id,
                                        "credit_id": self.cast_1.credit_id
                                    },
                                    "original_value": {
                                        "person_id": self.cast_1.person.id,
                                        "character": self.cast_1.character,
                                        "cast_id": self.cast_1.id,
                                        "credit_id": self.cast_1.credit_id
                                    }
                                },
                                {
                                    "id": "69151f818c84b2cc9c3a3d05",
                                    "action": TMDB_ACTIONS["updated"],
                                    "time": "2025-11-13 00:00:01 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "value": {
                                        "person_id": self.cast_2.person.id,
                                        "character": new_character_name_2,
                                        "cast_id": self.cast_2.id,
                                        "credit_id": self.cast_2.credit_id
                                    },
                                    "original_value": {
                                        "person_id": self.cast_2.person.id,
                                        "character": self.cast_2.character,
                                        "cast_id": self.cast_2.id,
                                        "credit_id": self.cast_2.credit_id
                                    }
                                },
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.cast_1.refresh_from_db()
            self.cast_2.refresh_from_db()
            self.assertEqual(self.cast_1.character, new_character_name_1)
            self.assertEqual(self.cast_2.character, new_character_name_2)

    def test_updated_origin_country(self):
        value = ["US"]
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "origin_country",
                            "items": [
                                {
                                    "id": "6915c1e7bdfe22a7d8876441",
                                    "action": TMDB_ACTIONS["updated"],
                                    "time": "2025-11-13 11:32:55 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "value": value,
                                    "original_value": [
                                        "UG",
                                        "US"
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.assertNotEqual(self.movie.origin_country, value)
            self.movie.refresh_from_db()
            self.assertEqual(self.movie.origin_country, value)

    def test_multiple_different_keys_different_actions(self):
        keyword_1_id = 1
        keyword_1_name = "keyword_1"
        keywords = [
                {
                    "id": keyword_1_id,
                    "name": keyword_1_name
                },
        ]
        self.movie.keywords = keywords
        self.movie.save()
        origin_country_value = ["US"]
        runtime_value = 75
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "genres",
                            "items": [
                                {
                                    "id": "691520e8535cb85e69ac20e3",
                                    "action": TMDB_ACTIONS["added"],
                                    "time": "2025-11-13 00:06:00 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "value": {
                                        "name": self.genre_1.name,
                                        "id": self.genre_1.id
                                    }
                                },
                            ]
                        },
                        {
                            "key": "origin_country",
                            "items": [
                                {
                                    "id": "6915c1e7bdfe22a7d8876441",
                                    "action": TMDB_ACTIONS["updated"],
                                    "time": "2025-11-13 11:32:55 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "value": origin_country_value,
                                    "original_value": [
                                        "UG",
                                        "US"
                                    ]
                                }
                            ]
                        },
                        {
                            "key": "plot_keywords",
                            "items": [
                                {
                                    "id": "6923a0157398caa33c1872ba",
                                    "action": TMDB_ACTIONS["deleted"],
                                    "time": "2025-11-24 00:00:21 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "original_value": {
                                        "name": keyword_1_name,
                                        "id": keyword_1_id
                                    }
                                },
                            ]
                        },
                        {
                            "key": "runtime",
                            "items": [
                                {
                                    "id": "69152701c4ea5b5c2e3a3f79",
                                    "action": TMDB_ACTIONS["updated"],
                                    "time": "2025-11-13 00:32:01 UTC",
                                    "iso_639_1": "pt",
                                    "iso_3166_1": "PT",
                                    "value": runtime_value,
                                    "original_value": 0
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.assertNotEqual(self.movie.origin_country, origin_country_value)
            self.assertNotEqual(self.movie.runtime, runtime_value)

            self.movie.refresh_from_db()

            genre_names = list(self.movie.genres.all().order_by("id").values_list("name", flat=True))
            expected = [self.genre_1.name]
            self.assertEqual(genre_names, expected)

            self.assertEqual(self.movie.origin_country, origin_country_value)

            keywords = list(map(ast.literal_eval, self.movie.keywords))
            expected = []
            self.assertEqual(keywords, expected)

            self.assertEqual(self.movie.runtime, runtime_value)

    def test_delete_runtime(self):
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "runtime",
                            "items": [
                                {
                                    "id": "69152701c4ea5b5c2e3a3f79",
                                    "action": TMDB_ACTIONS["updated"],
                                    "time": "2025-11-13 00:32:01 UTC",
                                    "iso_639_1": "pt",
                                    "iso_3166_1": "PT",
                                    "original_value": self.movie.runtime
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.movie.refresh_from_db()
            self.assertEqual(self.movie.runtime, None)

    def test_delete_title(self):
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "title",
                            "items": [
                                {
                                    "id": "69152701c4ea5b5c2e3a3f79",
                                    "action": TMDB_ACTIONS["deleted"],
                                    "time": "2025-11-13 00:32:01 UTC",
                                    "iso_639_1": "pt",
                                    "iso_3166_1": "PT",
                                    "original_value": self.movie.title
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.movie.refresh_from_db()
            self.assertEqual(self.movie.title, "")

    def test_destroyed_movie(self):
        responses = [
            self.movie_changes_response,
            {
                "body": {
                    "changes": [
                        {
                            "key": "general",
                            "items": [
                                {
                                    "id": "692452a26c2bacf11d0bad02",
                                    "action": TMDB_ACTIONS["destroyed"],
                                    "time": "2025-11-24 12:42:10 UTC",
                                    "iso_639_1": "",
                                    "iso_3166_1": "",
                                    "value": {
                                        "reason": "2"
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
        with stub_requests(self.tmdb, responses=responses):
            call_command("sync_movie_changes")
            self.assertFalse(Movie.objects.filter(id=self.movie.id).exists())
