from pyhub_ai.mixins.data_analyst import DataAnalysisAgentMixin
from pyhub_ai.specs import LLMModel

from .agent import AgentChatView


class DataAnalysisChatView(DataAnalysisAgentMixin, AgentChatView):
    """데이터 분석 채팅 컨슈머 클래스"""

    llm_model = LLMModel.OPENAI_GPT_4O
