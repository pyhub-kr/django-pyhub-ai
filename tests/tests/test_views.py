import json

import pytest
from bs4 import BeautifulSoup


@pytest.mark.asyncio
@pytest.mark.django_db
class TestAgentChatView:

    path = "/pyhub-ai/agent/chat/"

    @pytest.mark.it("HTMX 요청은 HTML SSE 응답을 받아야만 합니다.")
    async def test_htmx_sse_response(self, async_client, client):
        response = await async_client.post(
            self.path,
            data={"user_text": "대한민국의 수도는?"},
            headers={"HX-Request": "true"},
        )
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["Content-Type"]

        response_text = ""
        async for chunk in response.streaming_content:
            chunk_str = chunk.decode("utf-8")
            html_str = chunk_str.replace("data: ", "")  # "data: " 접두사가 있다면 제거

            soup = BeautifulSoup(html_str, "html.parser")

            # script 요소는 테스트할 필요가 없다고 판단해서 먼저 제거
            gen = (chunk_el.text for chunk_el in soup.select('script[type="x-template"]'))
            response_text += "".join(gen)

        assert "서울" in response_text

    @pytest.mark.it("헤더 지정이 없는 요청은 디폴트로 JSON SSE 응답을 처리되어야 합니다.")
    async def test_json_sse_response(self, async_client):
        response = await async_client.post(
            self.path,
            data={"user_text": "대한민국의 수도는?"},
            headers={"Accept": "application/json"},
        )
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["Content-Type"]

        async for chunk in response.streaming_content:
            chunk_str = chunk.decode("utf-8")
            json_str = chunk_str.replace("data: ", "")  # "data: " 접두사가 있다면 제거

            try:
                obj = json.loads(json_str)
                print(obj)
                assert len(obj) > 0
            except json.JSONDecodeError:
                pytest.fail("Failed to decode JSON response")
