from io import BytesIO
from typing import Any, Optional

from langchain.agents.output_parsers.tools import ToolAgentAction
from langchain_experimental.tools import PythonAstREPLTool as OrigPythonAstREPLTool
from matplotlib import pyplot as plt
from matplotlib import use as matplotlib_use

from .base.tools import PyhubToolMixin

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

    Attributes:
        figure_data (Optional[bytes]): 생성된 그래프의 바이너리 데이터.
            None인 경우 그래프가 생성되지 않았음을 의미합니다.

    Args:
        with_sns (bool): seaborn 라이브러리를 로드할지 여부. 기본값은 False입니다.
        with_pyplot (bool): pyplot을 로드할지 여부. 기본값은 False입니다.
        *args: 부모 클래스에 전달할 위치 인자들.
        **kwargs: 부모 클래스에 전달할 키워드 인자들.
    """

    figure_data: Optional[bytes] = None

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
            self.figure_data = buf.getvalue()

        return self.figure_data
