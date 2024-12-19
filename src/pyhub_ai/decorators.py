from asyncio import iscoroutinefunction
from functools import wraps
from urllib.parse import urlparse

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseNotAllowed
from django.shortcuts import resolve_url
from django.utils.log import log_response
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


def alogin_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    def decorator(view_func):
        @wraps(view_func)
        async def wrapper(request, *args, **kwargs):
            is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()

            if is_authenticated:
                return await view_func(request, *args, **kwargs)

            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]

            if (not login_scheme or login_scheme == current_scheme) and (
                not login_netloc or login_netloc == current_netloc
            ):
                path = request.get_full_path()

            from django.contrib.auth.views import redirect_to_login

            return redirect_to_login(path, resolved_login_url, redirect_field_name)

        return wrapper

    if function:
        return decorator(function)
    return decorator


def acsrf_exempt(view_func):
    # csrf_exempt 기본 장식자에 async 지원 추가

    if not iscoroutinefunction(view_func):
        return csrf_exempt(view_func)
    else:

        @wraps(view_func)
        async def wrapper_view(*args, **kwargs):
            return await view_func(*args, **kwargs)

        wrapper_view.csrf_exempt = True
        return wrapper_view


def arequire_http_methods(request_method_list):
    # require_http_methods 기본 장식자에 async 지원 추가

    def decorator(func):
        if not iscoroutinefunction(func):
            return require_http_methods(request_method_list)(func)
        else:

            @wraps(func)
            async def inner(request, *args, **kwargs):
                if request.method not in request_method_list:
                    response = HttpResponseNotAllowed(request_method_list)
                    log_response(
                        "Method Not Allowed (%s): %s",
                        request.method,
                        request.path,
                        response=response,
                        request=request,
                    )
                    return response
                return await func(request, *args, **kwargs)

            return inner

    return decorator


arequire_GET = arequire_http_methods(["GET"])
arequire_GET.__doc__ = "Decorator to require that an async view only accepts the GET method."

arequire_POST = arequire_http_methods(["POST"])
arequire_POST.__doc__ = "Decorator to require that an async view only accepts the POST method."

arequire_safe = arequire_http_methods(["GET", "HEAD"])
arequire_safe.__doc__ = "Decorator to require that an async view only accepts safe methods (GET and HEAD)."
