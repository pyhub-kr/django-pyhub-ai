from typing import Any, Dict, List, Optional, Union

from langchain_core.messages import AIMessage, HumanMessage

from pyhub_ai.agents import ChatAgent
from pyhub_ai.mixins import DataAnalystMixin
from pyhub_ai.specs import LLMModel
from pyhub_ai.tools.python import make_python_data_tool

from .agent import AgentChatConsumer


class DataAnalystChatConsumer(DataAnalystMixin, AgentChatConsumer):
    """데이터 분석 채팅 컨슈머 클래스"""

    llm_model = LLMModel.OPENAI_GPT_4O

    async def get_agent(
        self,
        previous_messages: Optional[List[Union[HumanMessage, AIMessage]]] = None,
    ) -> ChatAgent:
        df = self.get_dataframe()
        python_data_tool = make_python_data_tool(locals={"df": df})
        return ChatAgent(
            llm=self.get_llm(),
            system_prompt=self.get_llm_system_prompt(),
            tools=[python_data_tool],
            previous_messages=previous_messages,
            on_conversation_complete=self.on_conversation_complete,
            verbose=self.get_verbose(),
        )

    def get_llm_prompt_context_data(self) -> Dict[str, Any]:
        context_data = super().get_llm_prompt_context_data()
        context_data["dataframe_head"] = self.get_dataframe().head().to_markdown()
        context_data["column_guideline"] = self.get_column_guideline()
        return context_data
