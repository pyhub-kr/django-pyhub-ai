import json
from typing import Any, Awaitable, Callable, Literal, Optional, Union

from langchain.agents.output_parsers.tools import ToolAgentAction
from langchain_core.agents import AgentAction
from langchain_core.messages.ai import UsageMetadata

from pyhub_ai.blocks import ContentBlock, TextContentBlock


def make_tool_content_block_func(
    type: Literal["simple"] = "simple",
) -> Callable[
    [ToolAgentAction, Optional[Any], Optional[UsageMetadata]],
    Awaitable[Optional[ContentBlock]],
]:
    """도구 액션으로부터 콘텐츠 블록을 생성하는 콜백 함수를 생성하고 반환합니다.

    반환된 콜백 함수는 도구 액션을 처리하고 도구 실행 결과를 기반으로
    콘텐츠 블록을 생성합니다.

    Returns:
        callable: ToolAgentAction, observation, usage metadata를 인자로 받고
            Optional[ContentBlock]을 반환하는 비동기 콜백 함수입니다.
            콜백 함수는 다음과 같은 시그니처를 가집니다:
            async def aget_content_block(
                action: ToolAgentAction,
                observation: Optional[Any],
                usage_metadata: Optional[UsageMetadata]
            ) -> Optional[ContentBlock]
    """

    async def aget_content_block(
        action: Union[ToolAgentAction, AgentAction],  # 어떤 도구
        observation: Optional[Any],  # 도구 호출 결과 (호출 전에는 None)
        usage_metadata: Optional[UsageMetadata],  # usage
    ) -> Optional[ContentBlock]:
        tool_call_id = action.tool_call_id if isinstance(action, ToolAgentAction) else None

        if type == "simple":
            if observation is None:
                return TextContentBlock(id=tool_call_id, tool_name=action.tool)
            else:
                json_string = json.dumps(observation, indent=4, ensure_ascii=False)
                return TextContentBlock(
                    id=tool_call_id,
                    tool_name=action.tool,
                    value=f"""
`{action.tool}`

```
{json_string}
```
""".strip(),
                )
        else:
            # not implemented
            return TextContentBlock(role="error", value=f"지원되지 않는 type : {type}")

    return aget_content_block
