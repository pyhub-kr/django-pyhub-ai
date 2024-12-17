import os
from collections import defaultdict
from io import StringIO
from os.path import exists
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import httpx
import yaml
from django.conf import settings
from django.template.base import Template as DjangoTemplate
from django.template.context import Context as DjangoTemplateContext
from langchain_anthropic import ChatAnthropic
from langchain_community.llms.fake import FakeStreamingListLLM
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import BasePromptTemplate
from langchain_core.prompts.loading import load_prompt, load_prompt_from_config
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from ..agents import ChatAgent
from ..blocks import TextContentBlock
from ..specs import LLMModel
from ..utils import find_file_in_apps


class LLMMixin:
    llm_openai_api_key: SecretStr = ""
    llm_anthropic_api_key: SecretStr = ""
    llm_google_api_key: SecretStr = ""
    llm_system_prompt_path: Optional[Union[str, Path]] = None
    llm_system_prompt_template: Union[str, BasePromptTemplate, DjangoTemplate] = ""
    llm_prompt_context_data: Optional[Dict] = None
    llm_first_user_message_template: Optional[Union[str, DjangoTemplate]] = None
    llm_model: LLMModel = LLMModel.OPENAI_GPT_4O
    llm_temperature: float = 1
    llm_max_tokens: int = 4096
    llm_timeout: Union[float, Tuple[float, float]] = 5  # seconds
    llm_fake_responses: Optional[List[str]] = None

    def __init__(
        self,
        *args,
        llm_openai_api_key: Optional[SecretStr] = None,
        llm_anthropic_api_key: Optional[SecretStr] = None,
        llm_google_api_key: Optional[SecretStr] = None,
        llm_system_prompt_path: Optional[Union[str, Path]] = None,
        llm_system_prompt_template: Optional[Union[str, BasePromptTemplate, DjangoTemplate]] = None,
        llm_prompt_context_data: Optional[Dict] = None,
        llm_first_user_message_template: Optional[Union[str, DjangoTemplate]] = None,
        llm_model: Optional[LLMModel] = None,
        llm_temperature: Optional[float] = None,
        llm_max_tokens: Optional[int] = None,
        llm_timeout: Optional[Union[float, Tuple[float, float]]] = None,  # seconds
        llm_fake_responses: Optional[List[str]] = None,
        **kwargs,
    ):
        if llm_openai_api_key is not None:
            self.llm_openai_api_key = llm_openai_api_key
        if llm_anthropic_api_key is not None:
            self.llm_anthropic_api_key = llm_anthropic_api_key
        if llm_google_api_key is not None:
            self.llm_google_api_key = llm_google_api_key
        if llm_system_prompt_path is not None:
            self.llm_system_prompt_path = llm_system_prompt_path
        if llm_system_prompt_template is not None:
            self.llm_system_prompt_template = llm_system_prompt_template
        if llm_prompt_context_data is not None:
            self.llm_prompt_context_data = llm_prompt_context_data
        if llm_first_user_message_template is not None:
            self.llm_first_user_message_template = llm_first_user_message_template
        if llm_model is not None:
            self.llm_model = llm_model
        if llm_temperature is not None:
            self.llm_temperature = llm_temperature
        if llm_max_tokens is not None:
            self.llm_max_tokens = llm_max_tokens
        if llm_timeout is not None:
            self.llm_timeout = llm_timeout
        if llm_fake_responses is not None:
            self.llm_fake_responses = llm_fake_responses

        super().__init__(*args, **kwargs)

    def get_llm_openai_api_key(self) -> SecretStr:
        if self.llm_openai_api_key:
            return self.llm_openai_api_key

        api_key = getattr(settings, "OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
        return SecretStr(api_key)

    def get_llm_anthropic_api_key(self) -> SecretStr:
        if self.llm_anthropic_api_key:
            return self.llm_anthropic_api_key

        api_key = getattr(settings, "ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY", ""))
        return SecretStr(api_key)

    def get_llm_google_api_key(self) -> SecretStr:
        if self.llm_google_api_key:
            return self.llm_google_api_key

        api_key = getattr(settings, "GOOGLE_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))
        return SecretStr(api_key)

    def get_llm(self) -> BaseChatModel:
        if self.llm_fake_responses is not None:
            return FakeStreamingListLLM(responses=self.llm_fake_responses)

        llm_model = self.get_llm_model()

        if llm_model:
            llm_model_name = llm_model.name.upper()
            if llm_model_name.startswith("OPENAI_"):
                return ChatOpenAI(
                    openai_api_key=self.get_llm_openai_api_key(),
                    model_name=self.get_llm_model().value,
                    temperature=self.get_llm_temperature(),
                    max_tokens=self.get_llm_max_tokens(),
                    timeout=self.get_llm_timeout(),
                    streaming=True,
                    model_kwargs={"stream_options": {"include_usage": True}},
                )
            elif llm_model_name.startswith("ANTHROPIC_"):
                return ChatAnthropic(
                    anthropic_api_key=self.get_llm_anthropic_api_key(),
                    model=self.get_llm_model().value,
                    temperature=self.get_llm_temperature(),
                    max_tokens=self.get_llm_max_tokens(),
                    timeout=self.get_llm_timeout(),
                    streaming=True,
                )
            elif llm_model_name.startswith("GOOGLE_"):
                return ChatGoogleGenerativeAI(
                    google_api_key=self.get_llm_google_api_key(),
                    model=self.get_llm_model().value,
                    temperature=self.get_llm_temperature(),
                    max_tokens=self.get_llm_max_tokens(),
                    timeout=self.get_llm_timeout(),
                    streaming=True,
                )

        raise NotImplementedError(f"OpenAI API 만 지원하며, {llm_model}는 지원하지 않습니다.")

    def get_llm_system_prompt_path(self) -> Optional[Union[str, Path]]:
        return self.llm_system_prompt_path

    def get_llm_system_prompt_template(self) -> Union[str, BasePromptTemplate, DjangoTemplate]:
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

    def get_llm_prompt_context_data(self, **kwargs) -> Dict:
        if self.llm_prompt_context_data:
            # enum 타입 값에 대해 .value 속성으로 변환
            context_data = {k: v.value if hasattr(v, "value") else v for k, v in self.llm_prompt_context_data.items()}
        else:
            context_data = {}
        return dict(context_data, **kwargs)

    def get_llm_system_prompt(self, **kwargs) -> str:
        system_prompt_template = self.get_llm_system_prompt_template()
        context_data = self.get_llm_prompt_context_data(**kwargs)
        safe_data = defaultdict(lambda: "<키 누락>", context_data)

        if isinstance(system_prompt_template, DjangoTemplate):
            return system_prompt_template.render(DjangoTemplateContext(safe_data))
        else:
            return system_prompt_template.format(**safe_data).strip()

    def get_llm_first_user_message(self, **kwargs) -> Optional[str]:
        context_data = self.get_llm_prompt_context_data(**kwargs)
        if self.llm_first_user_message_template:
            safe_data = defaultdict(lambda: "<키 누락>", context_data)

            if isinstance(self.llm_first_user_message_template, DjangoTemplate):
                return self.llm_first_user_message_template.render(DjangoTemplateContext(safe_data))
            else:
                return self.llm_first_user_message_template.format_map(safe_data)
        return None

    def get_llm_model(self) -> LLMModel:
        return self.llm_model

    def get_llm_temperature(self) -> float:
        return self.llm_temperature

    def get_llm_max_tokens(self) -> int:
        return self.llm_max_tokens

    def get_llm_timeout(self) -> Union[float, Tuple[float, float]]:
        return self.llm_timeout
