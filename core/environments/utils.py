from project.settings import DJANGO_ENV


def is_development() -> bool:
    return DJANGO_ENV == "development"


def is_test() -> bool:
    return DJANGO_ENV == "test"


def is_production() -> bool:
    return DJANGO_ENV == "production"
