from pyhub_ai.specs import LLMModel

from ..mixins.data_analyst import DataAnalysisAgentMixin
from .agent import AgentChatConsumer


class DataAnalysisChatConsumer(DataAnalysisAgentMixin, AgentChatConsumer):
    """데이터 분석 채팅 컨슈머 클래스"""

    llm_model = LLMModel.OPENAI_GPT_4O


# 하위 호환성
DataAnalystChatConsumer = DataAnalysisChatConsumer
