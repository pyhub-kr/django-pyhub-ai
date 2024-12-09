from typing import List, Union

from langchain.agents.output_parsers import ToolsAgentOutputParser
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.outputs import Generation

from .agents import XAgentFinish


class XToolsAgentOutputParser(ToolsAgentOutputParser):

    def parse_result(self, result: List[Generation], *, partial: bool = False) -> Union[List[AgentAction], AgentFinish]:
        ret = super().parse_result(result, partial=partial)

        if isinstance(ret, AgentFinish):
            # AgentFinish에 usage_metadata 응답을 추가합니다.
            ai_message = ret.messages[0]
            if ai_message.usage_metadata is None:
                usage_metadata = result[0].message.usage_metadata

                return XAgentFinish(
                    return_values={"output": ai_message.content},  # noqa
                    log=str(ai_message.content),  # noqa
                    usage_metadata=usage_metadata,
                )

        return ret
