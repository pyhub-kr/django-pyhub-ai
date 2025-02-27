====================================
부록 #2. Anthropic API 응답 받기
====================================

Anthropic 응답이 좀 더 자연스럽습니다.

.. figure:: ./assets/anthropic/anthropic-response.png

    같은 프롬프트의 claude-3-7-sonnet-20250219 모델 응답


model 인자에 따른 API 호출 분기
=====================================

``chat/llm.py`` 파일의 ``LLM`` 클래스에서 ``model`` 인자에 따라 API 호출을 분기하여 응답을 생성합니다.

.. admonition:: ``chat/llm.py`` 파일 덮어쓰기
    :class: dropdown

    .. code-block:: python
        :linenos:
        :emphasize-lines: 1,11-13

        from typing import Dict, List, Optional, Literal, Union, cast

        from anthropic.types import ModelParam as AnthropicModelParam
        from django.conf import settings
        from anthropic import Anthropic
        from openai import OpenAI
        from openai.types import ChatModel as OpenAIChatModel
        from typing_extensions import TypeAlias

        # https://platform.openai.com/docs/models
        openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

        # https://docs.anthropic.com/en/docs/about-claude/models/all-models
        anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        # LLM Model Types
        LLMModelParams: TypeAlias = Union[str, AnthropicModelParam, OpenAIChatModel]


        class LLM:
            def __init__(
                self,
                model: LLMModelParams = "gpt-4o-mini",
                temperature: float = 0.2,
                max_tokens: int = 1000,
                system_prompt: str = "",
                initial_messages: Optional[List[Dict]] = None,
            ):
                self.model = model
                self.temperature = temperature
                self.max_tokens = max_tokens
                self.system_prompt = system_prompt
                self.history = initial_messages or []

            def make_reply(
                self,
                human_message: Optional[str] = None,
                model: Optional[LLMModelParams] = None,
            ):
                current_messages = [*self.history]
                current_model = model or self.model

                if human_message is not None:
                    current_messages.append({"role": "user", "content": human_message})

                try:
                    if "claude" in current_model.lower():
                        response = anthropic_client.messages.create(
                            model=cast(AnthropicModelParam, current_model),
                            system=self.system_prompt,
                            messages=current_messages,
                            temperature=self.temperature,
                            max_tokens=self.max_tokens,
                        )
                        ai_message = response.content[0].text
                    else:
                        response = openai_client.chat.completions.create(
                            model=cast(OpenAIChatModel, current_model),
                            messages=[
                                {
                                    "role": "system",
                                    "content": self.system_prompt,
                                },
                            ]
                            + current_messages,
                            temperature=self.temperature,
                            max_tokens=self.max_tokens,
                        )
                        ai_message = response.choices[0].message.content
                except Exception as e:
                    return f"API 호출에서 오류가 발생했습니다: {str(e)}"
                else:
                    self.history.extend(
                        [
                            {"role": "user", "content": human_message},
                            {"role": "assistant", "content": ai_message},
                        ]
                    )
                    return ai_message


LLM 인스턴스 생성 시에 anthropic 모델 지정
===============================================

이제 ``chat/views.py`` 파일에서 ``LLM`` 인스턴스 생성 시에 모델을 ``claude-3-7-sonnet-20250219`` 로 변경하면 Claude API를 호출하여 응답을 생성합니다.
anthropic에서 지원하는 모델은 https://docs.anthropic.com/en/docs/about-claude/models/all-models 공식문서에서 확인하실 수 있습니다.

.. code-block:: python
    :linenos:
    :emphasize-lines: 3

    llm = LLM(
        # model="gpt-4o-mini",
        model="claude-3-7-sonnet-20250219",
        temperature=1,
        system_prompt=system_prompt,
        initial_messages=messages,
    )
