from os.path import exists, splitext
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import pandas as pd
from langchain_core.tools import BaseTool

from pyhub_ai.mixins import AgentMixin
from pyhub_ai.tools import PyhubStructuredTool
from pyhub_ai.tools.python import make_python_data_tool
from pyhub_ai.utils import find_file_in_apps


class DataAnalysisMixin:
    """데이터 분석 믹스인 클래스"""

    dataframe_path: Optional[Union[Path, str]] = None
    column_guideline: str = ""

    def __init__(
        self, *args, dataframe_path: Optional[Union[Path, str]] = None, column_guideline: Optional[str] = None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        if dataframe_path is not None:
            self.dataframe_path = dataframe_path
        if column_guideline is not None:
            self.column_guideline = column_guideline

    def get_dataframe(self) -> pd.DataFrame:
        if getattr(self, "_dataframe", None) is None:
            dataframe_path = self.get_dataframe_path()
            if isinstance(dataframe_path, str) and dataframe_path.startswith(("http://", "https:/")):
                # pd.read_csv 에서 url 지원
                pass
            elif isinstance(dataframe_path, str):
                if not exists(dataframe_path):
                    dataframe_path = find_file_in_apps(dataframe_path, raise_exception=True)
                dataframe_path = Path(dataframe_path)
            if not dataframe_path:
                raise ValueError("데이터프레임 파일 경로가 설정되지 않았습니다.")

            if isinstance(dataframe_path, Path):
                extension = dataframe_path.suffix.lower()
            else:
                extension = splitext(dataframe_path)[-1].lower()

            if extension == ".csv":
                df = pd.read_csv(dataframe_path, encoding="utf-8")
            elif extension in (".xls", ".xlsx"):
                df = pd.read_excel(dataframe_path)
            else:
                raise ValueError(f"지원하지 않는 데이터프레임 파일 확장자: {extension}")

            setattr(self, "_dataframe", df)
        return getattr(self, "_dataframe")

    def get_dataframe_path(self) -> Optional[Union[str, Path]]:
        return self.dataframe_path

    def get_column_guideline(self) -> str:
        return self.column_guideline


class DataAnalysisAgentMixin(DataAnalysisMixin, AgentMixin):

    async def get_tools(self) -> List[Union[Callable, BaseTool]]:
        tools = await super().get_tools()
        tools.append(await self.get_python_data_tool())
        return tools

    async def get_python_data_tool(self) -> PyhubStructuredTool:
        df = self.get_dataframe()
        python_data_tool = make_python_data_tool(df)
        return python_data_tool

    async def aget_llm_prompt_context_data(self, **kwargs) -> Dict[str, Any]:
        context_data = await super().aget_llm_prompt_context_data(**kwargs)
        context_data["dataframe_head"] = self.get_dataframe().head().to_markdown()
        context_data["column_guideline"] = self.get_column_guideline()
        return context_data
