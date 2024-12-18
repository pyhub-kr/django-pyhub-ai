import logging
from io import BytesIO
from typing import Annotated, Any, AsyncIterator, Dict, List, Optional, Union

import pandas as pd
from langchain.agents.output_parsers.tools import ToolAgentAction
from langchain_core.agents import AgentAction, AgentStep
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, HumanMessage
from langchain_core.runnables.utils import AddableDict
from langchain_core.tools import BaseTool

from pyhub_ai.blocks import (
    CodeContentBlock,
    ContentBlock,
    DataFrameContentBlock,
    ImageDataContentBlock,
    TextContentBlock,
)
from pyhub_ai.tools import PyhubStructuredTool, tool_with_retry
from pyhub_ai.tools.python import PythonAstREPLTool
from pyhub_ai.utils import get_image_mimetype

from .chat import ChatAgent

logger = logging.getLogger(__name__)


class DataAnalystChatAgent(ChatAgent):
    """데이터 분석 대화 에이전트 클래스.

    ChatAgent를 상속하여 데이터프레임과 다양한 도구를 사용하여 대화형 데이터 분석을 수행합니다.

    Attributes:
        python_repl_tool (PythonAstREPLTool): 파이썬 REPL 도구로, 데이터프레임과 시각화 라이브러리를 로컬 환경에서 실행합니다.
    """

    def __init__(
        self,
        *args,
        df: pd.DataFrame,
        tools: Optional[List[BaseTool]] = None,
        **kwargs,
    ) -> None:
        # make_tool 내에서 매번 python repl tool이 생성되면, 각 tool이 독립적인 상태를 가지게 되어 값 공유가 되지 않습니다.
        # 현재 파이썬 프로세스에서 실행됩니다. 격리된 환경에서 실행할려면?
        locals_dict = {"df": df}
        self.python_repl_tool = PythonAstREPLTool(
            locals=locals_dict,
            with_sns=True,
            with_pandas=True,
        )

        if tools is None:
            tools = []

        # tools 지정을 통해 ChatAgent 내에서 AgentExecutor를 통해서 구동이 됩니다.
        # AgentExecutor를 통하면 도구 실행 결과를 관찰할 수 있지만 Chunk 단위 출력은 지원되지 않습니다.
        tools.append(self.make_python_repl_tool())

        super().__init__(*args, tools=tools, **kwargs)

    def make_python_repl_tool(self) -> BaseTool:
        """파이썬 REPL 도구를 생성합니다.

        Returns:
            BaseTool: 생성된 파이썬 REPL 도구.
        """

        async def python_repl_tool_aget_content_block(
            action: ToolAgentAction,
            observation: Optional[Any],
            usage_metadata: Optional[Any] = None,
        ) -> ContentBlock:
            if isinstance(observation, (pd.Series, pd.DataFrame)):
                return DataFrameContentBlock(value=observation)
            elif isinstance(observation, bytes):
                header = observation[:16]
                # 이미지가 아니라면 None 반환
                mimetype = get_image_mimetype(header)
                if mimetype:
                    return ImageDataContentBlock(value=observation, mimetype=mimetype)
                else:
                    return TextContentBlock(
                        role="error",
                        value=f"{repr(header)} 헤더의 데이터를 보여주는 기능이 없습니다.",
                    )
            else:
                code: str = action.tool_input.get("code")
                return CodeContentBlock(
                    value=code,
                    lang="python",
                    tool_name=action.tool,
                    usage_metadata=usage_metadata,
                )

        async def python_repl_tool_aget_observation(action: ToolAgentAction) -> Any:
            return await self.python_repl_tool.aget_observation(action)

        @tool_with_retry(
            aget_content_block=python_repl_tool_aget_content_block,
            aget_observation=python_repl_tool_aget_observation,
        )
        def python_repl_tool(code: Annotated[str, "실행할 파이썬 코드 (차트 생성용)"]):
            """파이썬, 판다스 쿼리, matplotlib, seaborn 코드를 실행하는 데 사용합니다."""
            return self.python_repl_tool.invoke(code)

        return python_repl_tool
