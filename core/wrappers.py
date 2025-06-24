import traceback
from functools import wraps
from http import HTTPMethod, HTTPStatus
from traceback import FrameSummary
from types import FunctionType

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from core.url.utils import is_url


def handle_exception(func_or_message: FunctionType | str, message: str = None, log=True):
    func = func_or_message if callable(func_or_message) else None
    message = func_or_message if not callable(func_or_message) else message

    def _wrapper(func):
        @wraps(func)
        def _wrapped_func(*args, **kwargs):
            try:
                if request := _find_first_by_klass(args, WSGIRequest):
                    args = list(args)
                    args.remove(request)
                    args = tuple(args)
                    return func(request, *args, **kwargs)
                return func(*args, **kwargs)
            except Exception as error:
                if request:
                    message = str(error)

                    if request.method == HTTPMethod.POST.value:
                        if is_url(message):
                            url = message
                            return redirect(url)

                        if request.headers.get("Accept") == "application/json":
                            return JsonResponse({
                                "status": HTTPStatus.INTERNAL_SERVER_ERROR.value,
                                "message": str(error),
                            })

                        messages.error(request, message)
                        if referer := request.META.get("HTTP_REFERER"):
                            return redirect(referer)
                        return redirect("/")
                    elif request.method == HTTPMethod.GET.value:
                        # TODO: This should depend on environment. Don't show message in production and test environments.
                        context = {
                            "message": message,
                            "headerless": True
                        }
                        return render(request, "core/error.html", context)
                if log:
                    tb = traceback.extract_tb(error.__traceback__, limit=-1)
                    fs: FrameSummary = tb[0]
                    # TODO: Replace all prints that could be shown in CI with logs
                    print(f"{fs.filename}, line {fs.lineno}")
                    print(f"{type(error).__name__}: {error}")
                if error is not Exception:
                    raise
                raise Exception(message)
        return _wrapped_func

    if func:
        return _wrapper(func)
    else:
        def _decorator(func):
           return _wrapper(func)
        return _decorator


def _find_first_by_klass(items: list, klass):
    return next((item for item in items if isinstance(item, klass)), None)
