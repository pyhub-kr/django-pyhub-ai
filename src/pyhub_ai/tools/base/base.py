import inspect
from typing import Callable, Dict, Literal, get_args, get_type_hints


def function_to_json(func: Callable) -> Dict:
    """
    주어진 함수에 대한 정보를 추출합니다. 함수의 이름, 설명, 매개변수 및 그 유형을 포함합니다.

    참고: https://github.com/openai/swarm/blob/main/swarm/util.py

    Args:
        func (callable): 정보를 추출할 함수.

    Returns:
        dict: 함수의 이름, 설명 및 매개변수를 포함하는 사전.
    """

    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        sig = inspect.signature(func)
    except ValueError as e:
        raise ValueError(f"Failed to get signature for function {func.__name__}: {str(e)}")

    kwargs_hints = get_type_hints(func)

    parameters = {}
    for param in sig.parameters.values():
        # Literal에 지정된 값 목록으로부터 인자의 타입을 추론합니다.
        if hasattr(param.annotation, "__origin__") and param.annotation.__origin__ is Literal:
            param_type = type_map.get(type(get_args(param.annotation)[0]), "string")
        else:
            param_type = type_map.get(param.annotation, "string")

        parameters[param.name] = {"type": param_type}

        arg_hints = kwargs_hints[param.name]
        literal = get_args(arg_hints)
        if literal:
            parameters[param.name]["enum"] = literal

    required = [param.name for param in sig.parameters.values() if param.default == inspect._empty]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": func.__doc__ or "",
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
                # properties에 없는 추가 속성은 허용하지 않습니다.
                "additionalProperties": False,
            },
            "strict": True,  # 구조화된 출력 요청
        },
    }
