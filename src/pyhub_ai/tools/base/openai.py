import asyncio
import inspect
import json
import sys
from typing import Any, AsyncGenerator, Callable, List, Optional, TypeVar

if sys.version_info[:2] < (3, 10):
    from typing_extensions import ParamSpec
else:
    # ParamSpec은 Python 3.10부터 typing 모듈에 포함
    from typing import ParamSpec

from openai.types.chat import ChatCompletionMessageToolCall

from .base import function_to_json

P = ParamSpec("P")  # 함수의 파라미터를 캡처하기 위한 ParamSpec
R = TypeVar("R")  # 함수의 반환 타입을 캡처하기 위한 TypeVar


class OpenAITools(list):
    def __init__(
        self,
        *functions: Callable,
        retry_strategy: Optional[Callable[[Callable[P, R]], Callable[P, R]]] = None,
    ):
        super().__init__()
        self.function_dict = {func.__name__: func for func in functions}
        self.extend([function_to_json(func) for func in self.function_dict.values()])
        self.retry_strategy = retry_strategy

    def get_func(self, func_name: str) -> Callable:
        return self.function_dict[func_name]

    async def call_func(self, tool_call: ChatCompletionMessageToolCall) -> Any:
        func_name = tool_call.function.name
        func = self.get_func(func_name)
        kwargs = json.loads(tool_call.function.arguments)

        if self.retry_strategy:
            func = self.retry_strategy(func)

        if inspect.iscoroutinefunction(func):
            return await func(**kwargs)
        else:
            return func(**kwargs)

    async def call_funcs(
        self, tool_calls: Optional[List[ChatCompletionMessageToolCall]] = None
    ) -> AsyncGenerator[Any, None]:
        if tool_calls is None:
            tool_calls = []

        results = await asyncio.gather(*(self.call_func(tool_call) for tool_call in tool_calls))
        for tool_call, result in zip(tool_calls, results):
            yield {
                "role": "tool",
                "content": json.dumps(result, ensure_ascii=False),
                "tool_call_id": tool_call.id,
            }
