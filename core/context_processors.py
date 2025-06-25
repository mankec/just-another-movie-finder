from core.sessions.utils import is_signed_in
from core.environments.utils import is_development, is_test, is_production


def is_signed_in_cp(request):
    return {
        'is_signed_in': is_signed_in(request.session)
    }


def is_development_cp(_request):
    return {
        "is_development": is_development()
    }


def is_test_cp(_request):
    return {
        "is_test": is_test()
    }


def is_production_cp(_request):
    return {
        "is_production": is_production()
    }
