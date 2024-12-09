import os
from collections import defaultdict
from io import StringIO
from os.path import exists
from pathlib import Path
from typing import Dict, Optional, Type, Union

import httpx
import yaml
from django.conf import settings
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import BasePromptTemplate
from langchain_core.prompts.loading import load_prompt, load_prompt_from_config
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from ..specs import LLMModel
from ..utils import find_file_in_apps


class LLMMixin:
    llm_openai_api_key: SecretStr = ""
    llm_system_prompt_path: Optional[Union[str, Path]] = None
    llm_system_prompt_template: Union[str, BasePromptTemplate] = ""
    llm_prompt_context_data: Optional[Dict] = None
    llm_first_user_message_template: Optional[str] = None
    llm_model: Type[LLMModel] = LLMModel.OPENAI_GPT_4O
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
                model_name=self.get_llm_model().value,
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

    def get_llm_model(self) -> Type[LLMModel]:
        return self.llm_model

    def get_llm_temperature(self) -> float:
        return self.llm_temperature

    def get_llm_max_tokens(self) -> int:
        return self.llm_max_tokens
