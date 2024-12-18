import os
from typing import Dict, Literal

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .utils import get_response


async def naver_map_router(
    start: str,
    goal: str,
    option: Literal["trafast", "tracomfort", "traoptimal", "traavoidtoll", "traavoidcaronly"],
) -> Dict:
    """네이버 지도 경로 검색 Direction 5 API를 사용하여 두 지점 간의 경로를 검색합니다.

    네이버 클라우드 플랫폼의 Maps Direction Driving API를 호출하여 출발지에서 목적지까지의
    경로 정보를 가져옵니다.

    Args:
        start: 출발지 좌표 (경도,위도)
        goal: 목적지 좌표 (경도,위도)
        option: 경로 탐색 옵션
            - trafast: 실시간 빠른길 (recommend)
            - tracomfort: 실시간 편한길
            - traoptimal: 실시간 최적
            - traavoidtoll: 무료 우선
            - traavoidcaronly: 자동차 전용도로 회피

    Returns:
        Dict: 경로 검색 결과를 포함하는 JSON 응답
            - code: 응답 코드 (0: 성공)
            - message: 응답 메시지
            - route: 경로 정보
                - [option]: 선택한 경로 옵션의 결과
                    - summary: 경로 요약 (거리, 시간, 요금 등)
                    - path: 경로 좌표 목록 [[경도, 위도], ...]
                    - section: 구간별 정보 (거리, 도로명, 혼잡도 등)
                    - guide: 경로 안내 정보 (안내 문구, 거리, 시간 등)

    References:
        - API 문서: https://api.ncloud-docs.com/docs/ai-naver-mapsdirections-driving
        - 설정: https://console.ncloud.com/naver-service/application
    """

    try:
        ncp_map_client_id = getattr(settings, "NCP_MAP_CLIENT_ID", None)
        ncp_map_client_secret = getattr(settings, "NCP_MAP_CLIENT_SECRET", None)
    except ImproperlyConfigured:
        ncp_map_client_id = None
        ncp_map_client_secret = None

    if ncp_map_client_id is None:
        ncp_map_client_id = os.environ.get("NCP_MAP_CLIENT_ID", None)

    if ncp_map_client_secret is None:
        ncp_map_client_secret = os.environ.get("NCP_MAP_CLIENT_SECRET", "")

    if not ncp_map_client_id or not ncp_map_client_secret:
        raise ValueError("NCP_MAP_CLIENT_ID 또는 NCP_MAP_CLIENT_SECRET이 설정되어 있지 않습니다.")

    api_url = "https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": ncp_map_client_id,
        "X-NCP-APIGW-API-KEY": ncp_map_client_secret,
    }
    params = {
        "start": start,
        "goal": goal,
        "option": option,
    }

    res = await get_response(api_url, params=params, headers=headers)
    return res.json()
