import re
from typing import Optional

import httpx
from httpx._types import HeaderTypes, QueryParamTypes


async def get_response(
    url: str,
    params: Optional[QueryParamTypes] = None,
    headers: Optional[HeaderTypes] = None,
) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params, headers=headers)
        res.raise_for_status()
        return res


def get_number_from_string(s: str) -> Optional[str]:
    """문자열에서 첫 번째로 발견되는 숫자를 추출합니다.

    Args:
        s: 숫자를 추출할 문자열

    Returns:
        str: 발견된 숫자 문자열
        None: 숫자가 발견되지 않은 경우
    """

    matched = re.search(r"\d+", s)
    if matched:
        return matched.group(0)
    return None


def remove_quotes(s: str) -> str:
    """문자열의 앞뒤 따옴표를 제거합니다.

    Args:
        s: 따옴표를 제거할 문자열

    Returns:
        str: 앞뒤 따옴표가 제거된 문자열
    """
    return re.sub(r"^['\"]|['\"]$", "", s)
