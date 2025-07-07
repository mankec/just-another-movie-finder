from core.sessions.constants import DEFAULT_SESSION_DATA
from core.sessions.utils import initialize_session

class InitializeSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        session = request.session
        if not session.keys():
            initialize_session(session)
        response = self.get_response(request)
        return response
