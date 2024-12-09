from typing import Any, Dict, List, Optional, Union

from langchain_core.messages import AIMessage, HumanMessage

from pyhub_ai.agents import DataAnalystChatAgent
from pyhub_ai.mixins import DataAnalystMixin
from pyhub_ai.views import AgentChatView


class DataAnalystChatView(DataAnalystMixin, AgentChatView):
    """데이터 분석 채팅 컨슈머 클래스"""

    async def get_agent(
        self,
        previous_messages: Optional[List[Union[HumanMessage, AIMessage]]] = None,
    ) -> DataAnalystChatAgent:
        return DataAnalystChatAgent(
            llm=self.get_llm(),
            df=self.get_dataframe(),
            system_prompt=self.get_llm_system_prompt(),
            previous_messages=previous_messages,
            on_conversation_complete=self.on_conversation_complete,
            verbose=self.get_verbose(),
        )

    def get_llm_prompt_context_data(self) -> Dict[str, Any]:
        context_data = super().get_llm_prompt_context_data()
        context_data["dataframe_head"] = self.get_dataframe().head().to_markdown()
        context_data["column_guideline"] = self.get_column_guideline()
        return context_data
