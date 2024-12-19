import logging
from typing import List, Optional

import pandas as pd

from pyhub_ai.tools import PyhubStructuredTool
from pyhub_ai.tools.python import make_python_data_tool

from .chat import ChatAgent

logger = logging.getLogger(__name__)


class DataAnalystChatAgent(ChatAgent):
    """데이터 분석 대화 에이전트 클래스.

    ChatAgent를 상속하여 데이터프레임과 다양한 도구를 사용하여 대화형 데이터 분석을 수행합니다.
    """

    def __init__(
        self,
        *args,
        df: pd.DataFrame,
        tools: Optional[List[PyhubStructuredTool]] = None,
        **kwargs,
    ) -> None:
        if tools is None:
            tools = []

        tools.append(make_python_data_tool(locals={"df": df}))

        super().__init__(*args, tools=tools, **kwargs)
