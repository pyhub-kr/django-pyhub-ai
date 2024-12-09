from base64 import b64decode, b64encode
from json import JSONDecoder, JSONEncoder
from typing import Any, Dict, List, Type

import pandas as pd
from langchain.agents.output_parsers.tools import ToolAgentAction
from langchain_core.agents import AgentActionMessageLog, AgentStep
from langchain_core.load import Serializable
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
)


def get_class_name(cls) -> str:
    is_class = isinstance(cls, type)
    if is_class:
        return cls.__name__
    return cls.__class__.__name__


class XJSONEncoder(JSONEncoder):
    def default(self, obj: Any) -> Dict:
        if isinstance(obj, bytes):
            return {"_type": "bytes", "_value": b64encode(obj).decode("utf-8")}

        elif isinstance(obj, pd.DataFrame):
            plain_obj = obj.to_dict()
            return {"_type": get_class_name(pd.DataFrame), "_value": plain_obj}

        elif isinstance(obj, pd.Series):
            plain_obj = obj.to_dict()
            return {"_type": get_class_name(pd.Series), "_value": plain_obj}

        elif getattr(obj, "model_dump", None) and callable(obj.model_dump):
            plain_obj = obj.model_dump(mode="python")

            # AgentStep.action 은 AgentAction 타입으로 지정되어 있습니다.
            # 그런데 model_dump 시에는 "type": "AgentActionMessageLog" 으로 변환되기에 (이유는?)
            # 다시 model_validate 시에는 아래 ValidationError가 발생합니다.
            # Input should be 'AgentAction' [type=literal_error, input_value='AgentActionMessageLog', input_type=str]
            # 그래서 호환되는 type 이름으로 변환해주는 작업이 필요합니다.
            if isinstance(obj, AgentStep):
                if plain_obj["action"]["type"] == "AgentActionMessageLog":
                    plain_obj["action"]["type"] = "AgentAction"

            return {"_type": get_class_name(obj), "_value": plain_obj}

        return super().default(obj)


class XJSONDecoder(JSONDecoder):
    pydantic_classes: List[Type[Serializable]] = [
        SystemMessage,
        HumanMessage,
        AIMessage,
        AIMessageChunk,
        FunctionMessage,
        ToolAgentAction,
        AgentActionMessageLog,
        AgentStep,
    ]
    pydantic_classes_dict: Dict[str, Type[Serializable]] = {get_class_name(cls): cls for cls in pydantic_classes}

    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, plain_obj: Any) -> Any:
        if isinstance(plain_obj, dict):
            # 위 JSONEncoder 를 통해 변환한 데이터를 다시 원래 형태로 변환합니다.
            if "_type" in plain_obj and "_value" in plain_obj:
                _type = plain_obj["_type"]
                _value = plain_obj["_value"]

                if _type == "bytes":
                    return b64decode(_value)

                elif _type == get_class_name(pd.DataFrame):
                    return pd.DataFrame.from_dict(_value)

                elif _type == get_class_name(pd.Series):
                    return pd.Series(_value)

                else:
                    try:
                        cls = self.pydantic_classes_dict[_type]
                        return cls.model_validate(_value)
                    except KeyError:
                        raise ValueError(f"Unknown object type: {type}")

        return plain_obj
