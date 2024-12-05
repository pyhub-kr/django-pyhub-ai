import logging
from collections import defaultdict
from typing import List, Optional, Union, AsyncIterator

from django.conf import settings
from django.core.files.base import File
from django.utils.html import format_html
from django.utils.safestring import SafeString
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import AddableDict

from pyhub_ai.blocks import TextContentBlock, ContentBlock
from pyhub_ai.mixins import LLMMixin

from ..agents.chat import ChatAgent
from ..models import ConversationMessage

from .base_chat import BaseChatConsumer


logger = logging.getLogger(__name__)


class AgentChatConsumer(LLMMixin, BaseChatConsumer):
    welcome_message_template = "챗봇 서비스에 오신 것을 환영합니다. ;)"
    show_initial_prompt: bool = True
    verbose: Optional[bool] = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent: Optional[ChatAgent] = None

    async def can_accept(self) -> bool:
        user = await self.get_user()
        if user and user.is_authenticated:
            return True
        return False

    async def on_accept(self) -> None:
        await super().on_accept()

        initial_messages = await self.get_initial_messages()

        # LLM history에는 Human/AI 메시지만 전달하고, Tools output은 전달하지 않습니다.
        self.agent = await self.get_agent(
            initial_messages=[msg for msg in initial_messages if isinstance(msg, (HumanMessage, AIMessage))]
        )

        message = self.get_welcome_message()
        if message:
            await self.render_block(TextContentBlock(role="notice", value=message))

        if self.get_show_initial_prompt():
            system_prompt = self.get_llm_system_prompt()
            if system_prompt:
                await self.render_block(TextContentBlock(role="system", value=system_prompt))

        if not initial_messages:
            user_message = self.get_llm_first_user_message()
            if user_message:
                if self.get_show_initial_prompt():
                    await self.render_block(TextContentBlock(role="user", value=user_message))
                await self.make_response(user_message)
        else:
            for lc_message in initial_messages:
                async for content_block in self.agent.translate_lc_message(lc_message):
                    await self.render_block(content_block)
                    usage_block = content_block.get_usage_block()
                    if usage_block:
                        await self.render_block(usage_block)

    def get_verbose(self) -> bool:
        if self.verbose is None:
            return settings.DEBUG
        return self.verbose

    async def get_agent(
        self,
        initial_messages: Optional[List[Union[HumanMessage, AIMessage]]] = None,
    ) -> ChatAgent:
        return ChatAgent(
            llm=self.get_llm(),
            system_prompt=self.get_llm_system_prompt(),
            initial_messages=initial_messages,
            on_conversation_complete=self.on_conversation_complete,
            verbose=self.get_verbose(),
        )

    async def think(
        self,
        input_query: str,
        files: Optional[List[File]] = None,
    ) -> AsyncIterator[ContentBlock]:
        async for chunk in self.agent.think(
            input_query=input_query,
            files=files,
        ):
            yield chunk

    async def get_initial_messages(self) -> List[Union[HumanMessage, AIMessage]]:
        conversation = await self.get_conversation()

        current_user = await self.get_user()
        if current_user and not current_user.is_authenticated:
            current_user = None

        return await ConversationMessage.objects.aget_histories(
            conversation=conversation,
            user=current_user,
        )

    async def on_conversation_complete(
        self,
        human_message: HumanMessage,
        ai_message: AIMessage,
        tools_output_list: Optional[List[AddableDict]] = None,
    ) -> None:
        conversation = await self.get_conversation()
        user = await self.get_user()

        if conversation is not None:
            await ConversationMessage.objects.aadd_messages(
                conversation=conversation,
                user=user,
                messages=[human_message] + (tools_output_list or []) + [ai_message],
            )

    def get_show_initial_prompt(self) -> bool:
        return self.show_initial_prompt

    def get_welcome_message_template(self) -> str:
        return self.welcome_message_template

    def get_welcome_message(self) -> SafeString:
        tpl = self.get_welcome_message_template().strip()
        context_data = self.get_llm_prompt_context_data()
        safe_data = defaultdict(lambda: "<키 지정 필요>", context_data)
        return format_html(tpl, **safe_data)
