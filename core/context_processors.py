from core.sessions.utils import is_signed_in
from project.settings import IS_DEVELOPMENT, IS_TEST, IS_PRODUCTION


def is_signed_in_cp(request):
    return {
        'is_signed_in': is_signed_in(request.session)
    }


def is_development_cp(_request):
    return {
        "is_development": IS_DEVELOPMENT,
    }


def is_test_cp(_request):
    return {
        "is_test": IS_TEST,
    }


def is_production_cp(_request):
    return {
        "is_production": IS_PRODUCTION,
    }
