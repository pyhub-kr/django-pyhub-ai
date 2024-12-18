import inspect
from functools import wraps
from typing import Any, Awaitable, Callable, Optional

from langchain.agents.output_parsers.tools import ToolAgentAction
from langchain_core.messages.ai import UsageMetadata

from pyhub_ai.blocks import ContentBlock

from .retry import default_retry_strategy
from .tools import PyhubStructuredTool


def tool_with_retry(
    name_or_callable=None,
    *args,
    retry_strategy=None,
    aget_content_block: Optional[
        Callable[
            [ToolAgentAction, Optional[Any], Optional[UsageMetadata]],
            Awaitable[ContentBlock],
        ]
    ] = None,
    aget_observation: Optional[Callable[[ToolAgentAction], Awaitable[Any]]] = None,
    **kwargs,
):
    """재시도 기능이 있는 도구를 생성하는 데코레이터.

    이 데코레이터는 함수를 PyhubStructuredTool로 변환하고 재시도 전략을 적용합니다.
    동기 및 비동기 함수 모두 지원합니다.

    Args:
        name_or_callable: 도구의 이름 또는 데코레이트할 함수. None이면 데코레이터 팩토리로 동작.
        *args: PyhubStructuredTool.from_function에 전달할 추가 인자.
        retry_strategy: 사용할 재시도 전략. None이면 기본 전략 사용.
        aget_content_block: 도구의 실행 결과를 ContentBlock으로 변환하는 비동기 함수.
        aget_observation: 도구의 실행 결과를 관찰 가능한 형태로 변환하는 비동기 함수.
        **kwargs: PyhubStructuredTool.from_function에 전달할 추가 키워드 인자.

    Returns:
        PyhubStructuredTool: 재시도 기능이 적용된 도구 객체.
        또는 데코레이터 함수(name_or_callable이 None인 경우).

    Examples:
        기본 사용법:
            @tool_with_retry
            def my_tool():
                pass

        매개변수와 함께 사용:
            @tool_with_retry(retry_strategy=custom_strategy)
            def my_tool():
                pass
    """
    used_retry_strategy = retry_strategy or default_retry_strategy

    if callable(name_or_callable) and not args and not kwargs:
        # @tool_with_retry 형식
        func = name_or_callable

        if inspect.iscoroutinefunction(func):
            param_func = None

            @used_retry_strategy
            @wraps(func)
            async def param_coroutine(*iargs, **ikwargs):
                return await func(*iargs, **ikwargs)

        else:

            @used_retry_strategy
            @wraps(func)
            def param_func(*iargs, **ikwargs):
                return func(*iargs, **ikwargs)

            param_coroutine = None

        return PyhubStructuredTool.from_function(
            func=param_func,
            coroutine=param_coroutine,
            name=func.__name__,
            description=func.__doc__ or "",
            aget_content_block=aget_content_block,
            aget_observation=aget_observation,
        )
    else:
        # @tool_with_retry(...) 형식
        def decorator(_func):
            if inspect.iscoroutinefunction(_func):
                _param_func = None

                @used_retry_strategy
                @wraps(_func)
                async def _param_coroutine(*iargs, **ikwargs):
                    return await func(*iargs, **ikwargs)

            else:

                @used_retry_strategy
                @wraps(_func)
                def _param_func(*iargs, **ikwargs):
                    return _func(*iargs, **ikwargs)

                _param_coroutine = None

            return PyhubStructuredTool.from_function(
                func=_param_func,
                coroutine=_param_coroutine,
                name=_func.__name__,
                description=_func.__doc__ or "",
                *args,
                aget_content_block=aget_content_block,
                aget_observation=aget_observation,
                **kwargs,
            )

        return decorator
