from project.auth.utils import is_signed_in


def is_signed_in_cp(request):
    return {
        'is_signed_in': is_signed_in(request.session)
    }
