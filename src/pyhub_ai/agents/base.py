from typing import Optional, Sequence

from langchain_core.agents import AgentFinish
from langchain_core.messages import BaseMessage
from langchain_core.messages.ai import AIMessage, UsageMetadata


class XAgentFinish(AgentFinish):
    usage_metadata: Optional[UsageMetadata] = None

    @property
    def messages(self) -> Sequence[BaseMessage]:
        """AgentFinish 에서는 content 속성만 가지기에, usage_metadata 속성을 추가합니다."""
        return [AIMessage(content=self.log, usage_metadata=self.usage_metadata)]
