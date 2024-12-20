# example/agents.py

from typing import Any, Optional

from langchain.agents.output_parsers.tools import ToolAgentAction
from langchain_core.messages.ai import UsageMetadata

from pyhub_ai.blocks import ContentBlock, TextContentBlock
from pyhub_ai.mixins import AgentMixin
from pyhub_ai.specs import LLMModel
from pyhub_ai.tools import tool_with_retry
from pyhub_ai.tools.yes24 import get_yes24_toc, search_yes24_books


async def aget_content_block(
    action: ToolAgentAction,  # 어떤 도구
    observation: Optional[Any],  # 도구 호출 결과 (호출 전에는 None)
    usage_metadata: Optional[UsageMetadata],  # usage
) -> ContentBlock:
    if observation is None:
        text = f"`{action.tool}` 호출 예정 : `{action.tool_input}`"
    else:
        text = f"`{action.tool}` 호출 완료 : `{action.tool_input}`"

    return TextContentBlock(value=text)


class BestsellerMakrerAgentManager(AgentMixin):
    llm_model = LLMModel.OPENAI_GPT_4O_MINI
    llm_temperature = 0
    # https://platform.openai.com/playground/chat?models=gpt-4o
    tools = [
        tool_with_retry(search_yes24_books, aget_content_block=aget_content_block),
        tool_with_retry(get_yes24_toc, aget_content_block=aget_content_block),
    ]
    llm_system_prompt_template = """
1. [keyword] 키워드로 도서 목록을 검색해줘.
2. 각 도서들의 목차를 모두 읽어온 후에,
3. 종합해서 내가 앞으로 집필할 베스트셀러의 목차를 작성해줘.
4. 목차 구성에 맞게 markdown list 포맷으로 정리해줘."""
