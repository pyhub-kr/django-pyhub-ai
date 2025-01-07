import logging
from collections import defaultdict
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

from django.conf import settings
from django.core.files.base import File
from django.utils.safestring import SafeString
from langchain.tools import BaseTool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import AddableDict

from pyhub_ai.agents.chat import ChatAgent
from pyhub_ai.blocks import ContentBlock, TextContentBlock
from pyhub_ai.models import ConversationMessage
from pyhub_ai.utils import format_map_html

from .chat import ChatMixin
from .llm import LLMMixin

logger = logging.getLogger(__name__)


T = TypeVar("T", bound="AgentMixin")


class AgentMixin(LLMMixin, ChatMixin):
    welcome_message_template = ""
    show_initial_prompt: bool = True
    verbose: Optional[bool] = None
    tools: Optional[List[Union[Callable, BaseTool]]] = None

    def __init__(self, *args, tools: Optional[List[Union[Callable, BaseTool]]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent: Optional[ChatAgent] = None
        self.param_tools = tools

    async def get_tools(self) -> List[Union[Callable, BaseTool]]:
        """에이전트가 사용할 도구 목록을 가져옵니다.

        Returns:
            List[Union[Callable, BaseTool]]: 클래스에 정의된 도구 목록. 정의되지 않은 경우 빈 리스트 반환

        Note:
            이 메서드는 클래스 레벨에서 정의된 tools 속성을 반환합니다.
        """
        return self.__class__.tools or []

    async def get_agent(self, previous_messages: Optional[List[Union[HumanMessage, AIMessage]]] = None) -> ChatAgent:
        """ChatAgent 인스턴스를 생성하고 반환합니다.

        Args:
            previous_messages: 이전 대화 메시지 목록. HumanMessage와 AIMessage 인스턴스들의 리스트

        Returns:
            ChatAgent: 설정된 ChatAgent 인스턴스

        Note:
            생성된 ChatAgent는 LLM, 시스템 프롬프트, 이전 메시지 기록, 도구 등으로 초기화됩니다.
        """
        _tools = await self.get_tools() + (self.param_tools or [])
        params = await self.get_agent_params()
        return ChatAgent(
            previous_messages=previous_messages,
            tools=_tools,
            **params,
        )

    async def get_agent_params(self) -> Dict[str, Any]:
        return {
            "llm": self.get_llm(),
            "spec": self.get_llm_spec(),
            "system_prompt": await self.aget_llm_system_prompt(),
            "on_conversation_complete": self.on_conversation_complete,
            "verbose": self.get_verbose(),
        }

    async def agent_setup(self, render_previous_messages: bool = True):
        previous_messages = await self.aget_previous_messages()

        # LLM history에는 Human/AI 메시지만 전달하고, Tools output은 전달하지 않습니다.
        self.agent = await self.get_agent(
            previous_messages=[msg for msg in previous_messages if isinstance(msg, (HumanMessage, AIMessage))]
        )

        if render_previous_messages:
            # 대화내역 존재유무에 상관없이, 환영메시지가 있다면 노출합니다.
            welcome_message = await self.aget_welcome_message()
            if welcome_message:
                await self.render_block(TextContentBlock(role="notice", value=welcome_message))

            # 시스템 프롬프트 노출 플래그가 설정되어있다면 시스템 프롬프트를 노출합니다.
            if self.get_show_initial_prompt():
                system_prompt = await self.aget_llm_system_prompt()
                if system_prompt:
                    await self.render_block(TextContentBlock(role="system", value=system_prompt))

        # 저장된 대화내역이 없고,
        if not previous_messages:
            # 설정된 첫 User 메시지가 있다면 LLM에게 전달하고 응답을 렌더링합니다.
            first_user_message = await self.aget_llm_first_user_message()
            if first_user_message:
                if self.get_show_initial_prompt():
                    await self.render_block(TextContentBlock(role="user", value=first_user_message))
                await self.make_response(first_user_message)
        # 저장된 대화내역이 있다면, 대화 내역을 노출합니다.
        else:
            if render_previous_messages:
                await self.render_messages(previous_messages)

        return self

    async def think(self, input_query: str, files: Optional[List[File]] = None) -> AsyncIterator[ContentBlock]:
        async for chunk in self.agent.think(input_query=input_query, files=files):
            yield chunk

    async def on_conversation_complete(
        self,
        human_message: HumanMessage,
        ai_message: AIMessage,
        tools_output_list: Optional[List[AddableDict]] = None,
    ) -> None:
        conversation = await self.aget_conversation()
        user = await self.get_user()

        if conversation is not None:
            await ConversationMessage.objects.aadd_messages(
                conversation=conversation,
                user=user,
                messages=[human_message] + (tools_output_list or []) + [ai_message],
            )

    async def aget_previous_messages(self) -> List[Union[HumanMessage, AIMessage]]:
        conversation = await self.aget_conversation()

        current_user = await self.get_user()
        if current_user and not current_user.is_authenticated:
            current_user = None

        return await ConversationMessage.objects.aget_histories(conversation=conversation, user=current_user)

    async def render_messages(self, messages):
        for lc_message in messages:
            async for content_block in self.agent.translate_lc_message(lc_message):
                await self.render_block(content_block)
                usage_block = content_block.get_usage_block()
                if usage_block:
                    await self.render_block(usage_block)

    def get_welcome_message_template(self) -> str:
        return self.welcome_message_template

    async def aget_welcome_message(self) -> SafeString:
        tpl = self.get_welcome_message_template().strip()
        context_data = await self.aget_llm_prompt_context_data()
        safe_data = defaultdict(lambda: "<키 지정 필요>", context_data)
        return format_map_html(tpl, **safe_data)

    def get_show_initial_prompt(self) -> bool:
        return self.show_initial_prompt

    def get_verbose(self) -> bool:
        if self.verbose is None:
            return settings.DEBUG
        return self.verbose
