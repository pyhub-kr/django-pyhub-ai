import inspect
from typing import Any, Awaitable, Callable, Optional

from langchain.agents.output_parsers.tools import ToolAgentAction
from langchain_core.messages.ai import UsageMetadata
from langchain_core.tools import StructuredTool

from pyhub_ai.blocks import ContentBlock


class PyhubToolMixin:
    """Pyhub 도구를 위한 믹스인 클래스.

    이 클래스는 도구에 콘텐츠 블록과 관찰 기능을 추가하는 믹스인을 제공합니다.

    Attributes:
        _custom_aget_content_block: 콘텐츠 블록을 생성하는 커스텀 비동기 함수.
        _custom_aget_observation: 관찰을 수행하는 커스텀 비동기 함수.
    """

    def __init__(self, *args, **kwargs) -> None:
        """PyhubToolMixin을 초기화합니다.

        Args:
            *args: 부모 클래스에 전달할 위치 인자.
            **kwargs: 부모 클래스에 전달할 키워드 인자.
        """
        super().__init__(*args, **kwargs)
        self._custom_aget_content_block = None
        self._custom_aget_observation = None

    async def aget_content_block(
        self,
        action: ToolAgentAction,
        observation: Optional[Any],
        usage_metadata: Optional[UsageMetadata] = None,
    ) -> Optional[ContentBlock]:
        """도구 실행 결과를 ContentBlock으로 변환합니다.

        Args:
            action: 도구 실행 액션.
            observation: 도구 실행 결과.
            usage_metadata: 사용량 메타데이터.

        Returns:
            ContentBlock 또는 None: 변환된 콘텐츠 블록. 변환할 수 없는 경우 None.
        """
        if self._custom_aget_content_block is not None:
            params = {}
            sig = inspect.signature(self._custom_aget_content_block)
            if "action" in sig.parameters:
                params["action"] = action
            if "observation" in sig.parameters:
                params["observation"] = observation
            if "usage_metadata" in sig.parameters:
                params["usage_metadata"] = usage_metadata

            if inspect.iscoroutinefunction(self._custom_aget_content_block):
                return await self._custom_aget_content_block(**params)
            else:
                return self._custom_aget_content_block(**params)
        return None

    async def aget_observation(self, action: ToolAgentAction) -> Optional[Any]:
        """도구 실행 결과를 관찰합니다.

        Args:
            action: 도구 실행 액션.

        Returns:
            Any 또는 None: 관찰 결과. 관찰할 수 없는 경우 None.
        """
        if self._custom_aget_observation is not None:
            params = {}
            sig = inspect.signature(self._custom_aget_observation)
            if "action" in sig.parameters:
                params["action"] = action

            if inspect.iscoroutinefunction(self._custom_aget_observation):
                return await self._custom_aget_observation(**params)
            else:
                return self._custom_aget_observation(**params)
        return None


class PyhubStructuredTool(PyhubToolMixin, StructuredTool):
    """Pyhub 구조화된 도구 클래스.

    StructuredTool을 확장하여 콘텐츠 블록과 관찰 기능을 추가합니다.
    """

    @classmethod
    def from_function(
        cls,
        *args,
        aget_content_block: Optional[
            Callable[
                [ToolAgentAction, Optional[Any], Optional[UsageMetadata]],
                Awaitable[ContentBlock],
            ]
        ] = None,
        aget_observation: Optional[Callable[[ToolAgentAction], Awaitable[Any]]] = None,
        **kwargs: Any,
    ) -> "PyhubStructuredTool":
        """함수로부터 PyhubStructuredTool 인스턴스를 생성합니다.

        Args:
            *args: 부모 클래스의 from_function에 전달할 위치 인자.
            aget_content_block: 콘텐츠 블록을 생성하는 비동기 함수.
            aget_observation: 관찰을 수행하는 비동기 함수.
            **kwargs: 부모 클래스의 from_function에 전달할 키워드 인자.

        Returns:
            PyhubStructuredTool: 생성된 도구 인스턴스.
        """
        obj = super().from_function(*args, **kwargs)
        if aget_content_block is not None:
            obj._custom_aget_content_block = aget_content_block
        if aget_observation is not None:
            obj._custom_aget_observation = aget_observation
        return obj
