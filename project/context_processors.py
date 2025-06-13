from project.utils.session_utils import is_signed_in


def is_signed_in_cp(request):
    return {
        'is_signed_in': is_signed_in(request.session)
    }
