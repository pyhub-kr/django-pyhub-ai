from io import BytesIO
from typing import Annotated, Any, Dict, Optional

import pandas as pd
from langchain.agents.output_parsers.tools import ToolAgentAction
from langchain_experimental.tools import PythonAstREPLTool as OrigPythonAstREPLTool
from matplotlib import pyplot as plt
from matplotlib import use as matplotlib_use

from pyhub_ai.blocks import (
    CodeContentBlock,
    ContentBlock,
    DataFrameContentBlock,
    ImageDataContentBlock,
    TextContentBlock,
)
from pyhub_ai.utils import get_image_mimetype

from .base.decorators import tool_with_retry
from .base.tools import PyhubStructuredTool, PyhubToolMixin

"""파이썬 AST REPL 도구 모듈.

이 모듈은 파이썬 코드를 실행하고 matplotlib 그래프를 생성하는 도구를 제공합니다.
비 GUI 환경에서 그래프를 생성하고 저장하는 기능을 포함합니다.

참고:
    matplotlib 백엔드 옵션:
    - Agg: 래스터 그래픽을 생성하는 백엔드로, 파일로 이미지 저장을 주로 할 때 사용합니다.
           서버 환경에서 유용하며, PNG, JPG, SVG, PDF 등으로 저장할 수 있습니다.
    - PDF: PDF 파일을 생성하는 백엔드로, 고품질의 PDF 파일을 생성할 수 있습니다.
    - SVG: SVG 파일을 생성하는 백엔드로, 웹에 최적화된 벡터 파일 형식인 SVG를 생성합니다.
    - PS: 포스트스크립트 파일을 생성하는 백엔드로, 고품질 인쇄용 그래픽에 적합합니다.
"""


# 비 GUI 백엔드를 지정 (서버 환경에 적합)
matplotlib_use("Agg")

# interactive 모드 비활성화
plt.ioff()


class PythonAstREPLTool(PyhubToolMixin, OrigPythonAstREPLTool):
    """파이썬 AST REPL 도구 클래스.

    이 클래스는 파이썬 코드를 실행하고 matplotlib 그래프를 생성하는 기능을 제공합니다.
    seaborn과 pyplot을 선택적으로 사용할 수 있습니다.

    Args:
        with_sns (bool): seaborn 라이브러리를 로드할지 여부. 기본값은 False입니다.
        with_pyplot (bool): pyplot을 로드할지 여부. 기본값은 False입니다.
        *args: 부모 클래스에 전달할 위치 인자들.
        **kwargs: 부모 클래스에 전달할 키워드 인자들.
    """

    def __init__(self, *args, with_sns: bool = False, with_pyplot: bool = False, **kwargs):
        super().__init__(*args, **kwargs)

        if with_sns:
            import seaborn as sns

            self.locals["sns"] = sns

        if with_pyplot:
            self.locals["plt"] = plt

    async def aget_observation(self, action: ToolAgentAction) -> Optional[Any]:
        """도구 실행 결과를 관찰하고 그래프 데이터를 반환합니다.

        plt.show()가 호출된 경우 현재 그래프를 이미지로 저장하고 해당 데이터를 반환합니다.

        Args:
            action (ToolAgentAction): 실행할 도구 액션.

        Returns:
            Optional[Any]: 그래프가 생성된 경우 이미지 데이터, 그렇지 않은 경우 None.
        """
        param = tuple(action.tool_input.values())[0]

        # matplotlib 이미지가 생성되었다면
        if "plt.show" in param:
            # 위 파이썬 코드가 exec로 현재 파이썬 인터프리터를 통해 실행되기 때문에,
            # plt.gcf()로 현재 figure 객체를 가져올 수 있습니다.
            fig: plt.Figure = plt.gcf()
            buf = BytesIO()
            fig.savefig(buf, format="jpeg")
            fig.clear()
            return buf.getvalue()

        return None


def make_python_data_tool(df: pd.DataFrame) -> PyhubStructuredTool:
    """파이썬 데이터 분석 REPL 도구를 생성합니다.

    Returns:
        PyhubStructuredTool: 생성된 파이썬 REPL 도구.
    """

    # make_tool 내에서 매번 python repl tool이 생성되면, 각 tool이 독립적인 상태를 가지게 되어 값 공유가 되지 않습니다.
    # 현재 파이썬 프로세스에서 실행됩니다. 격리된 환경에서 실행할려면?
    lc_python_ast_repl_tool = PythonAstREPLTool(locals={"df": df}, with_sns=True, with_pyplot=True)

    async def python_repl_tool_aget_content_block(
        action: ToolAgentAction,
        observation: Optional[Any],
        usage_metadata: Optional[Any] = None,
    ) -> ContentBlock:
        if isinstance(observation, (pd.Series, pd.DataFrame)):
            return DataFrameContentBlock(value=observation)
        elif isinstance(observation, bytes):
            header = observation[:16]
            # 이미지가 아니라면 None 반환
            mimetype = get_image_mimetype(header)
            if mimetype:
                return ImageDataContentBlock(value=observation, mimetype=mimetype)
            else:
                return TextContentBlock(
                    role="error",
                    value=f"{repr(header)} 헤더의 데이터를 보여주는 기능이 없습니다.",
                )
        else:
            code: str = action.tool_input.get("code")
            return CodeContentBlock(
                value=code,
                lang="python",
                tool_name=action.tool,
                usage_metadata=usage_metadata,
            )

    async def python_repl_tool_aget_observation(action: ToolAgentAction) -> Any:
        return await lc_python_ast_repl_tool.aget_observation(action)

    @tool_with_retry(
        aget_content_block=python_repl_tool_aget_content_block,
        aget_observation=python_repl_tool_aget_observation,
    )
    def python_repl_tool(code: Annotated[str, "Python code to execute (for chart generation)"]):
        """Used to execute Python code, Pandas queries, matplotlib and seaborn visualizations."""
        return lc_python_ast_repl_tool.invoke(code)

    return python_repl_tool
