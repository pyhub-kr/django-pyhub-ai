from collections import defaultdict
import logging
import os
from io import StringIO
from os.path import exists
from pathlib import Path
from typing import List, Optional, Union, Dict, AsyncIterator

import httpx
import yaml
from django.apps import apps
from django.conf import settings
from django.core.files.base import File
from django.utils.html import format_html
from django.utils.safestring import SafeString
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import BasePromptTemplate, load_prompt
from langchain_core.prompts.loading import load_prompt_from_config
from langchain_core.runnables import AddableDict
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from ..agents.chat import ChatAgent, ContentBlock
from ..blocks import TextContentBlock
from ..models import ConversationMessage
from ..specs import LLMModel

from .base_chat import BaseChatConsumer


logger = logging.getLogger(__name__)


PYHUB_AI_APP_DIR = Path(__file__).resolve().parent.parent


def find_file_in_apps(*paths: Union[str, Path]) -> Path:
    """주어진 경로에서 파일을 찾아 반환합니다.

    먼저 PYHUB_AI_APP_DIR에서 파일을 찾고, 없으면 설치된 모든 Django 앱에서 순차적으로 검색합니다.

    Args:
        *paths: 찾고자 하는 파일의 경로 구성요소들. str 또는 Path 객체.

    Returns:
        Path: 찾은 파일의 전체 경로

    Raises:
        FileNotFoundError: 주어진 경로에서 파일을 찾을 수 없는 경우
    """

    path = PYHUB_AI_APP_DIR.joinpath(*paths)
    if path.exists():
        return path

    for app_config in apps.get_app_configs():
        path = Path(app_config.path).joinpath(*paths)
        if path.exists():
            return path

    raise FileNotFoundError(f"{paths} 경로의 파일을 찾을 수 없습니다.")


class LLMMixin:
    llm_openai_api_key: SecretStr = ""
    llm_system_prompt_path: Optional[Union[str, Path]] = None
    llm_system_prompt_template: Union[str, BasePromptTemplate] = ""
    llm_prompt_context_data: Optional[Dict] = None
    llm_first_user_message_template: Optional[str] = None
    llm_model: LLMModel = LLMModel.OPENAI_GPT_4O
    llm_temperature: float = 1
    llm_max_tokens: int = 4096

    def get_llm_openai_api_key(self) -> SecretStr:
        if self.llm_openai_api_key:
            return self.llm_openai_api_key

        api_key = getattr(settings, "OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
        return SecretStr(api_key)

    def get_llm(self) -> BaseChatModel:
        llm_model_name = self.get_llm_model().name.upper()
        if llm_model_name.startswith("OPENAI_"):
            return ChatOpenAI(
                openai_api_key=self.get_llm_openai_api_key(),
                model_name=self.get_llm_model(),
                temperature=self.get_llm_temperature(),
                max_tokens=self.get_llm_max_tokens(),
                streaming=True,
                model_kwargs={"stream_options": {"include_usage": True}},
            )

        raise NotImplementedError(f"OpenAI API 만 지원하며, {llm_model_name}는 현재 지원하지 않습니다.")

    def get_llm_system_prompt_path(self) -> Optional[Union[str, Path]]:
        return self.llm_system_prompt_path

    def get_llm_system_prompt_template(self) -> Union[str, BasePromptTemplate]:
        system_prompt_path = self.get_llm_system_prompt_path()
        if system_prompt_path:
            if isinstance(system_prompt_path, str) and system_prompt_path.startswith(("http://", "https:/")):
                res = httpx.get(system_prompt_path)
                config = yaml.safe_load(StringIO(res.text))
                system_prompt_template = load_prompt_from_config(config)
            else:
                if isinstance(system_prompt_path, str):
                    if not exists(system_prompt_path):
                        system_prompt_path = find_file_in_apps(system_prompt_path)

                system_prompt_template: BasePromptTemplate = load_prompt(system_prompt_path, encoding="utf-8")
            return system_prompt_template
        return self.llm_system_prompt_template

    def get_llm_prompt_context_data(self) -> Dict:
        if self.llm_prompt_context_data:
            return self.llm_prompt_context_data
        return {}

    def get_llm_system_prompt(self) -> str:
        system_prompt_template = self.get_llm_system_prompt_template()
        context_data = self.get_llm_prompt_context_data()
        safe_data = defaultdict(lambda: "<키 지정 필요>", context_data)
        return system_prompt_template.format(**safe_data).strip()

    def get_llm_first_user_message(self) -> Optional[str]:
        context_data = self.get_llm_prompt_context_data()
        if self.llm_first_user_message_template:
            safe_data = defaultdict(lambda: "<키 지정 필요>", context_data)
            return self.llm_first_user_message_template.format_map(safe_data)
        return None

    def get_llm_model(self) -> LLMModel:
        return self.llm_model

    def get_llm_temperature(self) -> float:
        return self.llm_temperature

    def get_llm_max_tokens(self) -> int:
        return self.llm_max_tokens


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
