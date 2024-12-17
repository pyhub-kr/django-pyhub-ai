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


def tool_with_retry(*tool_args, retry_strategy=None, **tool_kwargs):
    # 인자가 없는 경우(예: @tool_with_retry) 바로 함수가 전달될 수 있음
    # 이 경우 tool_args[0]이 바로 함수일 가능성이 있음
    if len(tool_args) == 1 and callable(tool_args[0]) and retry_strategy is None and not tool_kwargs:
        func = tool_args[0]
        used_retry_strategy = default_retry_strategy

        @wraps(func)
        def inner(*args, **kwargs):
            return used_retry_strategy(func)(*args, **kwargs)

        # @tool과 동일한 기능을 제공하기 위해 tool()을 적용
        return orig_tool()(inner)

    # @tool_with_retry(...) 형태일 경우
    if retry_strategy is None:
        retry_strategy = default_retry_strategy

    def decorator(func):
        wrapped_func = retry_strategy(func)

        @wraps(func)
        def inner(*args, **kwargs):
            return wrapped_func(*args, **kwargs)

        return orig_tool(*tool_args, **tool_kwargs)(inner)

    return decorator
