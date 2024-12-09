import logging
from io import BytesIO
from typing import Annotated, AsyncIterator, Dict, List, Optional, Union

import pandas as pd
import seaborn as sns
from langchain.agents.output_parsers.tools import ToolAgentAction
from langchain_core.agents import AgentAction, AgentStep
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, HumanMessage
from langchain_core.runnables.utils import AddableDict
from langchain_core.tools import BaseTool, tool
from langchain_experimental.tools import PythonAstREPLTool
from matplotlib import pyplot as plt
from matplotlib import use as matplotlib_use

from pyhub_ai.blocks import (
    CodeContentBlock,
    ContentBlock,
    DataFrameContentBlock,
    ImageDataContentBlock,
    TextContentBlock,
)
from pyhub_ai.utils import get_image_mimetype

from .chat import ChatAgent

logger = logging.getLogger(__name__)


# 비 GUI 백엔드를 지정 (서버 환경에 적합)
#  - Agg: 래스터 그래픽을 생성하는 백엔드로, 파일로 이미지 저장을 주로 할 때 사용합니다.
#         서버 환경에서 유용하며, PNG, JPG, SVG, PDF 등으로 저장할 수 있습니다.
#  - PDF: PDF 파일을 생성하는 백엔드로, 고품질의 PDF 파일을 생성할 수 있습니다.
#  - SVG: SVG 파일을 생성하는 백엔드로, 웹에 최적화된 벡터 파일 형식인 SVG를 생성합니다.
#  - PS: 포스트스크립트 파일을 생성하는 백엔드로, 고품질 인쇄용 그래픽에 적합합니다.
matplotlib_use("Agg")

# interactive 모드 비활성화
plt.ioff()


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
        locals_dict = {"df": df, "sns": sns, "plt": plt}
        self.python_repl_tool = PythonAstREPLTool(locals=locals_dict)

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

        @tool
        def python_repl_tool(code: Annotated[str, "실행할 파이썬 코드 (차트 생성용)"]):
            """파이썬, 판다스 쿼리, matplotlib, seaborn 코드를 실행하는 데 사용합니다."""
            return self.python_repl_tool.invoke(code)

        return python_repl_tool

    async def aquery(
        self,
        human_message: HumanMessage,
    ) -> AsyncIterator[Union[AIMessageChunk, AddableDict]]:
        """LLM 응답 스트림을 후처리하여 반환합니다."""

        chunk_message: Union[AIMessageChunk, AddableDict]

        async for chunk_message in super().aquery(human_message):
            # python_repl_tool 도구를 통해 생성된 이미지를 읽어들여
            # steps observation에 이미지 데이터를 추가합니다.
            if isinstance(chunk_message, AddableDict):
                agent_output: AddableDict = chunk_message
                if "steps" in agent_output:
                    agent_step_list: List[AgentStep] = agent_output["steps"]
                    for agent_step in agent_step_list:
                        if agent_step.action.tool == "python_repl_tool":
                            code = agent_step.action.tool_input["code"]

                            # matplotlib 이미지가 생성되었다면
                            if "plt.show" in code:
                                # 위 파이썬 코드가 exec로 현재 파이썬 인터프리터를 통해 실행되기 때문에,
                                # plt.gcf()로 현재 figure 객체를 가져올 수 있습니다.
                                fig: plt.Figure = plt.gcf()
                                buf = BytesIO()
                                fig.savefig(buf, format="jpeg")
                                fig.clear()
                                agent_step.observation = buf.getvalue()

            yield chunk_message

    async def translate_lc_message(
        self,
        lc_message: Union[BaseMessage, AddableDict, dict],
    ) -> AsyncIterator[ContentBlock]:
        async for current_content_block in super().translate_lc_message(lc_message):
            if not isinstance(current_content_block, (AddableDict, dict)):
                yield current_content_block

            # DataAnalystChatAgent 관심사 AddableDict 타입에 대해서만 처리
            else:
                agent_output: AddableDict = current_content_block

                #
                # 출력 내용
                #   - ref: [랭체인 LangChain 노트] 에이전트
                #          https://wikidocs.net/262586
                #
                # Action
                #   - actions : AgentAction 또는 그 하위 클래스
                #   - messages: 액션 호출에 해당하는 채팅 메시지
                #
                # Observation
                #   - steps : 현재 액션과 그 관찰을 포함한 에이전트가 지금까지 수행한 작업의 기록
                #   - messages : 함수 호출 결과(즉, 관찰)를 포함한 채팅 메시지
                #
                # Final Answer
                #   - output : AgentFinish
                #   - messages : 최종 출력을 포함한 채팅 메시지
                #
                # 최종 목표가 달성될 때까지 Action/Observation을 반복하고, 최종 응답을 출력합니다.
                # Action -> Observation -> Action -> Observation -> ... -> Final Answer
                #

                # Action 단계 : 도구 실행 계획 (아직 도구 실행 전)
                if "actions" in agent_output:
                    action_list: List[Union[AgentAction, ToolAgentAction]]
                    action_list = agent_output["actions"]
                    for action in action_list:
                        usage_metadata = None

                        if action.message_log:
                            ai_message_chunk = action.message_log[0]
                            if isinstance(ai_message_chunk, AIMessage):
                                usage_metadata = ai_message_chunk.usage_metadata

                        if agent_output["messages"]:
                            ai_message_chunk = agent_output["messages"][0]
                            if isinstance(ai_message_chunk, AIMessage):
                                usage_metadata = ai_message_chunk.usage_metadata

                        if action.tool == "python_repl_tool":
                            tool_kwargs: Dict = action.tool_input
                            code: str = tool_kwargs.get("code")
                            # code를 tool을 통해 실행할 예정
                            yield CodeContentBlock(
                                value=code,
                                lang="python",
                                tool_name=action.tool,
                                usage_metadata=usage_metadata,
                            )
                        else:
                            yield TextContentBlock(
                                role="error",
                                value=f"출력 구현이 필요한 도구 ({action.tool}) : {repr(action)}",
                                usage_metadata=usage_metadata,
                            )

                # Observation 단계 : 에이전트가 수행한 단계들의 리스트이며, 도구 실행 결과를 관찰할 때 생성됩니다.
                if "steps" in agent_output:
                    agent_step_list: List[AgentStep] = agent_output["steps"]
                    for agent_step in agent_step_list:
                        observation = agent_step.observation

                        if isinstance(observation, (pd.Series, pd.DataFrame)):
                            yield DataFrameContentBlock(value=observation)

                        # 에러 메시지일 경우에만 에러 메시지를 출력
                        elif isinstance(observation, str) and "error" in observation.lower():
                            yield TextContentBlock(role="error", value=observation)

                        elif not observation:
                            pass

                        elif isinstance(observation, bytes):
                            header = observation[:16]
                            # 이미지가 아니라면 None 반환
                            mimetype = get_image_mimetype(header)
                            if mimetype:
                                yield ImageDataContentBlock(value=observation, mimetype=mimetype)

                        else:
                            yield TextContentBlock(
                                role="error",
                                value=f"구현되지 않은 관찰 ({type(observation)}) : {repr(observation)}",
                            )

                # Final Answer 단계
                if "output" in agent_output:
                    # output에는 응답 문자열만 있고 메타 데이터가 없습니다.
                    # messages 리스트 내의 AIMessage 객체를 활용하겠습니다.
                    ai_message: AIMessage
                    for ai_message in agent_output["messages"]:
                        yield TextContentBlock(
                            role="assistant",
                            value=ai_message.content,
                            usage_metadata=ai_message.usage_metadata,
                        )

                # 대화 기록이 업데이트될 때 : AIMessageChunk, FunctionMessage, AIMessage
                # if "messages" in output:
                #     pass
