import logging
import traceback
from typing import Any, AsyncIterator, Awaitable, Callable, List, Optional, Union

import openai
from django.core.files import File
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_tool_messages
from langchain.agents.output_parsers.tools import ToolAgentAction
from langchain_core.agents import AgentAction
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.messages.ai import AIMessage, AIMessageChunk
from langchain_core.prompts import (
    BasePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.prompts.chat import BaseMessagePromptTemplate
from langchain_core.runnables import AddableDict, Runnable, RunnablePassthrough
from langchain_core.tools import BaseTool, StructuredTool

from pyhub_ai.blocks import (
    ContentBlock,
    ImageDataContentBlock,
    ImageUrlContentBlock,
    TextContentBlock,
)
from pyhub_ai.parsers import XToolsAgentOutputParser
from pyhub_ai.tools import PyhubStructuredTool, tool_with_retry
from pyhub_ai.utils import encode_image_files, get_image_mimetype, sum_and_merge_dicts

logger = logging.getLogger(__name__)


class ChatAgent:
    """채팅 에이전트 클래스.

    Attributes:
        INPUT_MESSAGES_KEY (str): 입력 메시지 키.
    """

    HISTORY_MESSAGES_KEY = "history"
    INPUT_MESSAGES_KEY = "input"

    def __init__(
        self,
        llm: BaseChatModel,
        system_prompt: Union[str, BasePromptTemplate],
        previous_messages: Optional[List[Union[HumanMessage, AIMessage]]] = None,
        tools: Optional[List[Union[Callable, BaseTool]]] = None,
        on_conversation_complete: Optional[
            Callable[[HumanMessage, AIMessage, Optional[List[AddableDict]]], Awaitable[None]]
        ] = None,
        max_iterations: int = 20,
        max_execution_time: int = 60,
        handle_parsing_errors: bool = True,
        verbose: bool = False,
    ):
        """ChatAgent의 초기화 메서드.

        Args:
            llm (BaseChatModel): 대형 언어 모델.
            system_prompt (Union[str, BasePromptTemplate]): 시스템 프롬프트.
            previous_messages (Optional[List[Union[HumanMessage, AIMessage]]]): 초기 메시지 목록.
            tools (Optional[List[Union[Callable, BaseTool]]): 사용할 도구 목록.
            on_conversation_complete (Optional[Callable[[HumanMessage, AIMessage], None]]): 메시지가 완성되면 호출할 콜백 함수.
            max_iterations (int): 최대 반복 횟수. tools 옵션을 사용할 때만 사용됩니다.
            max_execution_time (int): 최대 실행 시간. tools 옵션을 사용할 때만 사용됩니다.
            handle_parsing_errors (bool): 파싱 오류 처리 여부. tools 옵션을 사용할 때만 사용됩니다.
            verbose (bool): 상세 로그 출력 여부.
        """

        base_messages: List[Union[BaseMessage, BaseMessagePromptTemplate]] = []

        if system_prompt:
            base_messages.append(SystemMessage(system_prompt))

        if previous_messages:
            base_messages.extend(previous_messages)

        base_messages.extend(
            (
                MessagesPlaceholder(variable_name=self.HISTORY_MESSAGES_KEY),
                # 아래 방식을 사용하면, list/dict 형식의 데이터가 문자열로 변환되어 전송되기에
                # LLM에서도 dict 내의 이미지 데이터를 읽어들이지 못합니다.
                # ("human", "{" + self.INPUT_MESSAGES_KEY + "}"),
                # 아래처럼 MessagesPlaceholder를 활용하면 문자열 변환되지 않고
                # list/dict 타입 그대로 LLM에게 전송되어 LLM에서 이미지 데이터를 이미지로서 처리할 수 있게 됩니다.
                MessagesPlaceholder(variable_name=self.INPUT_MESSAGES_KEY),
            )
        )

        # 랭체인 툴 @tool 장식자로 래핑되지 않은 함수에 대해서는
        # @tool_with_retry 장식자로 래핑시켜줍니다.
        self.tools = []
        for _tool in tools or []:
            if isinstance(_tool, StructuredTool):
                self.tools.append(_tool)
            else:
                self.tools.append(tool_with_retry(_tool))

        self.tools_dict = {tool.name: tool for tool in self.tools}

        if not self.tools:
            prompt = ChatPromptTemplate.from_messages(base_messages)
            runnable = (prompt | llm).with_config(verbose=verbose)
        else:
            # Agent를 통하기 때문에 stream 옵션을 지정하더라도 Agent를 경유하여 응답이 생성되기에,
            # 스트리밍 방식으로 응답 생성이 불가능하고 한 번에 모든 응답이 생성됩니다.
            # create_tool_calling_agent 에서는 ToolsAgentOutputParser 가 적용되어있고,
            # 이를 적용하면 AgentFinish 응답에서 usage_metadata 항목이 누락됩니다.
            # create_tool_calling_agent 에서는 output parser 지정 옵션이 없기에
            # create_tool_calling_agent 구현을 아래에 복사하여 사용하고 output parser 만 변경하여 사용합니다.

            prompt = ChatPromptTemplate.from_messages(
                (
                    *base_messages,
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                )
            )

            agent = (
                RunnablePassthrough.assign(agent_scratchpad=lambda x: format_to_tool_messages(x["intermediate_steps"]))
                | prompt
                | llm.bind_tools(self.tools)
                | XToolsAgentOutputParser()
            )

            runnable = AgentExecutor(
                agent=agent,
                tools=self.tools,
                handle_parsing_errors=handle_parsing_errors,
                max_iterations=max_iterations,
                max_execution_time=max_execution_time,
                verbose=verbose,
            )

        self.runnable: Runnable = runnable
        self.messages_history: List[BaseMessage] = []
        self.on_conversation_complete = on_conversation_complete

    async def aquery(
        self,
        human_message: HumanMessage,
    ) -> AsyncIterator[Union[AIMessageChunk, AddableDict]]:
        """LLM 응답 스트림을 후처리하여 반환합니다.

        matplotlib 이미지가 생성된 경우 이미지 데이터를 추출하여 agent_step.observation에 저장합니다.

        Args:
            human_message: 사용자 입력 메시지

        Yields:
            Union[AIMessageChunk, AddableDict]: LLM의 응답 청크 또는 에이전트 실행 결과
                - AIMessageChunk: LLM의 텍스트 응답 청크
                - AddableDict: 에이전트 실행 결과 (도구 사용 결과 포함)

        Raises:
            RuntimeError: matplotlib 이미지 처리 중 오류 발생 시
        """
        chunk_message: Union[AIMessageChunk, AddableDict]

        # anthropic api 호출에서는 입력되자마자 입력 token 수가 생성되고,
        # 출력 token 수는 출력이 완료되고 나서 따로 출력되기에
        # 이를 합산해서 마지막에 출력합시다.
        usage_chunk_message_list = []

        async for chunk_message in self.runnable.astream(
            input={
                self.HISTORY_MESSAGES_KEY: self.messages_history,
                self.INPUT_MESSAGES_KEY: [human_message],
            },
        ):
            # fake llm 사용 시에는 chunk_message 타입이 AIMessageChunk가 아니라 문자열
            if getattr(chunk_message, "usage_metadata", None) is None:
                if isinstance(chunk_message, AddableDict):
                    agent_output = chunk_message
                    if "steps" in agent_output:
                        agent_step_list: List[AgentStep] = agent_output["steps"]
                        for agent_step in agent_step_list:
                            action = agent_step.action

                            # 등록된 Tool에서 aget_observation() 반환값이 있다면 호출하여
                            if action.tool in self.tools_dict:
                                tool = self.tools_dict[action.tool]
                                if isinstance(tool, PyhubStructuredTool):
                                    ob = await tool.aget_observation(action)
                                    if ob is not None:
                                        agent_step.observation = ob

                yield chunk_message

            else:
                usage_chunk_message_list.append(chunk_message)

        if usage_chunk_message_list:
            last_chunk_message = usage_chunk_message_list[-1]
            last_chunk_message.usage_metadata = sum_and_merge_dicts(
                *(chunk_message.usage_metadata for chunk_message in usage_chunk_message_list)
            )
            yield last_chunk_message

    async def think(
        self,
        input_query: str,
        files: Optional[List[File]] = None,
    ) -> AsyncIterator[Union[ContentBlock, AddableDict]]:
        """LLM에 쿼리하고 응답을 ContentBlock 스트림으로 변환합니다.

        Args:
            input_query: 사용자 입력 텍스트
            files: 이미지 파일 목록. 이미지와 함께 쿼리할 때 사용됨

        Returns:
            AsyncIterator[Union[ContentBlock, AddableDict]]: ContentBlock 또는 AddableDict 스트림
                - ContentBlock: 텍스트, 이미지 등의 컨텐츠를 표현하는 블록
                - AddableDict: 도구 실행 결과를 포함하는 딕셔너리

        Raises:
            openai.RateLimitError: OpenAI API 호출 한도 초과 시
            Exception: 기타 예외 발생 시
        """
        image_urls: Optional[List[str]] = None

        if not files:
            human_message = HumanMessage(input_query)
        else:
            image_urls = encode_image_files(files, max_size=256, quality=60)
            human_message = HumanMessage(
                content=[
                    {"type": "text", "text": input_query},
                    *[
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": url,
                                "detail": "auto",  # low, high, auto
                            },
                        }
                        for url in image_urls
                    ],
                ]
            )

        # ChatAgent 관심사 AIMessageChunk 타입 외에는 그대로 yield
        chunk_message: Union[AIMessageChunk, AddableDict]

        is_first_chunk = True

        ai_message_chunk_list: List[AIMessageChunk] = []
        tools_output_list: List[AddableDict] = []
        try:
            async for chunk_message in self.aquery(human_message):
                if is_first_chunk:
                    if image_urls:
                        for url in image_urls:
                            yield ImageUrlContentBlock(role="user", value=url)
                    is_first_chunk = False

                async for current_msg in self.translate_lc_message(chunk_message):
                    yield current_msg

                if isinstance(chunk_message, AIMessageChunk):
                    ai_message_chunk_list.append(chunk_message)
                elif isinstance(chunk_message, AddableDict):
                    tools_output_list.append(chunk_message)
                else:
                    logger.warning(f"지원되지 않는 메시지 타입: {type(chunk_message)}")

            ai_message: Optional[AIMessage] = None

            if ai_message_chunk_list:
                assert (
                    len({chunk.id for chunk in ai_message_chunk_list}) == 1
                ), "ID가 다른 AIMessageChunk가 섞여 있습니다."

                ai_message_id = ai_message_chunk_list[0].id
                ai_message_str = "".join([chunk.content for chunk in ai_message_chunk_list])
                usage_metadata = ai_message_chunk_list[-1].usage_metadata
                ai_message = AIMessage(
                    id=ai_message_id,
                    content=ai_message_str,
                    usage_metadata=usage_metadata,
                )

            if tools_output_list:
                if "output" in tools_output_list[-1]:
                    # tools 출력에서 output을 제거하고 AIMessage로 변환하여 저장합니다.
                    agent_output = tools_output_list.pop()

                    if agent_output["messages"]:
                        if ai_message is not None:
                            logger.warning(f"기존 AIMessage({ai_message})를 덮어쓰기 합니다.")
                        ai_message = agent_output["messages"][0]

            if ai_message is not None:
                self.messages_history.extend((human_message, ai_message))

                if self.on_conversation_complete:
                    await self.on_conversation_complete(human_message, ai_message, tools_output_list)

        except openai.RateLimitError as e:
            logger.error(f"Rate limit error: {e}")
            yield TextContentBlock(role="error", value=e.message)
        except Exception as e:
            logger.error(f"Error: {e}")
            logger.error(traceback.format_exc())
            yield TextContentBlock(role="error", value=str(e))

    async def translate_lc_message(
        self,
        lc_message: Union[BaseMessage, AddableDict],
    ) -> AsyncIterator[ContentBlock]:
        """Langchain 메시지를 ContentBlock으로 변환합니다.

        Args:
            lc_message: 변환할 Langchain 메시지. BaseMessage 또는 AddableDict 타입.

        Yields:
            ContentBlock: 변환된 ContentBlock 객체.
                - SystemMessage -> TextContentBlock (role="system")
                - HumanMessage -> TextContentBlock/ImageUrlContentBlock (role="user")
                - AIMessage/AIMessageChunk -> TextContentBlock (role="assistant")
                - 기타 메시지는 그대로 반환

        Raises:
            없음. 에러 발생시 에러 메시지를 담은 TextContentBlock을 yield합니다.
        """

        if isinstance(lc_message, SystemMessage):
            yield TextContentBlock(
                id=lc_message.id,
                role="system",
                value=lc_message.content,
            )
        elif isinstance(lc_message, HumanMessage):
            if isinstance(lc_message.content, str):
                yield TextContentBlock(
                    id=lc_message.id,
                    role="user",
                    value=lc_message.content,
                )
            elif isinstance(lc_message.content, list):
                for sub_content in lc_message.content:
                    if sub_content["type"] == "image_url":
                        yield ImageUrlContentBlock(
                            role="user",
                            value=sub_content["image_url"]["url"],  # noqa
                        )
                    elif sub_content["type"] == "text":
                        yield TextContentBlock(
                            id=lc_message.id,
                            role="user",
                            value=sub_content["text"],
                        )
                    else:
                        yield TextContentBlock(
                            id=lc_message.id,
                            role="user",
                            value=sub_content,
                        )
            else:
                yield TextContentBlock(
                    role="error",
                    value=f"지원되지 않는 HumanMessage 형식: {type(lc_message.content)}",
                )
        elif isinstance(lc_message, (AIMessage, AIMessageChunk)):
            yield TextContentBlock(
                id=lc_message.id,
                role="assistant",
                value=lc_message.content,
                usage_metadata=lc_message.usage_metadata,
            )
        elif isinstance(lc_message, (AddableDict, dict)):
            agent_output: AddableDict = lc_message

            # Action 단계 : Tool 도구 실행 계획 (아직 도구 실행 전)
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

                    if isinstance(action, ToolAgentAction):
                        if action.tool in self.tools_dict:
                            tool: PyhubStructuredTool = self.tools_dict[action.tool]
                            block = await tool.aget_content_block(
                                action,
                                None,
                                usage_metadata=usage_metadata,
                            )
                            if block is not None:
                                yield block
                        else:
                            logger.warning(f"[actions] {action.tool} Tool을 tools_dict에서 찾을 수 없습니다.")

            # Observation 단계 : Tool 실행 반환값
            if "steps" in agent_output:
                agent_step_list: List[AgentStep] = agent_output["steps"]
                for agent_step in agent_step_list:
                    action: ToolAgentAction = agent_step.action
                    observation = agent_step.observation
                    block = await self.translate_observation(action, observation)
                    if block is not None:
                        yield block

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

        else:
            # 관심사 이외 메시지는 그대로 yield
            yield lc_message

    async def translate_observation(self, action: ToolAgentAction, observation: Any) -> Optional[ContentBlock]:

        if action.tool in self.tools_dict:
            tool = self.tools_dict[action.tool]
            if isinstance(tool, PyhubStructuredTool):
                return await tool.aget_content_block(action, observation)
            else:
                logger.warning(f"[observation] {action.tool}을 PyhubStructuredTool 기반으로 변경해주세요.")
                return None
        else:
            logger.warning(f"[observation] {action.tool} Tool을 tools_dict에서 찾을 수 없습니다.")

        # 에러 메시지일 경우에만 에러 메시지를 출력
        if isinstance(observation, str) and "error" in observation.lower():
            return TextContentBlock(role="error", value=observation)

        elif not observation:
            pass

        elif isinstance(observation, bytes):
            header = observation[:16]
            # 이미지가 아니라면 None 반환
            mimetype = get_image_mimetype(header)
            if mimetype:
                return ImageDataContentBlock(value=observation, mimetype=mimetype)

        return None
