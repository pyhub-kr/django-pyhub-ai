from typing import Any, Dict, List, Optional, Union

from django.template.base import Template as DjangoTemplate

from pyhub_ai.agents import ChatAgent
from pyhub_ai.blocks import TextContentBlock
from pyhub_ai.mixins import LLMMixin
from pyhub_ai.specs import LLMModel


class Brain(LLMMixin):
    @classmethod
    async def aquery(
        cls,
        user_text: str,
        model: Optional[LLMModel] = None,
        system_prompt_template: Optional[Union[str, DjangoTemplate]] = None,
        prompt_context_data: Optional[Dict[str, Any]] = None,
        fake_responses: Optional[List[str]] = None,
        verbose: bool = False,
    ) -> str:
        self = cls(
            llm_model=model,
            llm_system_prompt_template=system_prompt_template,
            llm_prompt_context_data=prompt_context_data,
            llm_fake_responses=fake_responses,
        )

        llm = self.get_llm()
        system_prompt = self.get_llm_system_prompt()

        agent = ChatAgent(
            llm=llm,
            system_prompt=system_prompt,
            verbose=verbose,
        )

        output_text = ""
        async for content_block in agent.think(input_query=user_text):
            if isinstance(content_block, TextContentBlock):
                output_text += content_block.value
            # FakeStreamingListLLM 을 사용할 경우,
            elif isinstance(content_block, str):
                output_text += content_block
            else:
                raise TypeError(f"Unknown content type: {type(content_block)}")

        return output_text
