from asyncio import iscoroutinefunction
from functools import wraps

from django.http import HttpResponseNotAllowed
from django.utils.log import log_response
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


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
