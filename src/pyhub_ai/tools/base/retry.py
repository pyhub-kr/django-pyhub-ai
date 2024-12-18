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
