import inspect
from functools import wraps

from langchain.tools import tool as orig_tool
from tenacity import RetryCallState, retry, stop_after_attempt, wait_random


def retry_error_callback_to_string(retry_state: RetryCallState) -> str:
    exc = retry_state.outcome.exception()
    return f"Exception: {exc.__class__.__name__}: {exc}"


default_retry_strategy = retry(
    # 모든 예외에 대해서 재시도. 특정 예외 클래스만 지정하고 싶다면?
    # retry=retry_if_exception_type(Value),
    stop=stop_after_attempt(3),  # 재시도 횟수
    wait=wait_random(1, 3),  # 재시도 대기 시간
    retry_error_callback=retry_error_callback_to_string,
)


def tool_with_retry(name_or_callable=None, *args, retry_strategy=None, **kwargs):
    if callable(name_or_callable) and not args and not kwargs:
        # @tool_with_retry 형식
        func = name_or_callable
        used_retry_strategy = retry_strategy or default_retry_strategy

        if inspect.iscoroutinefunction(func):

            @orig_tool()
            @used_retry_strategy
            @wraps(func)
            async def inner(*iargs, **ikwargs):
                return await func(*iargs, **ikwargs)

        else:

            @orig_tool()
            @used_retry_strategy
            @wraps(func)
            def inner(*iargs, **ikwargs):
                return func(*iargs, **ikwargs)

        return inner

    # @tool_with_retry(...) 형식
    def decorator(func):
        used_retry_strategy = retry_strategy or default_retry_strategy
        if inspect.iscoroutinefunction(func):

            @orig_tool(name_or_callable, *args, **kwargs)
            @used_retry_strategy
            @wraps(func)
            async def inner(*iargs, **ikwargs):
                return await func(*iargs, **ikwargs)

        else:

            @orig_tool(name_or_callable, *args, **kwargs)
            @used_retry_strategy
            @wraps(func)
            def inner(*iargs, **ikwargs):
                return func(*iargs, **ikwargs)

        return inner

    return decorator
