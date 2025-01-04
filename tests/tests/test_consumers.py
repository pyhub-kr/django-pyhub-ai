import asyncio
from typing import AsyncGenerator

import pytest
from channels.testing import WebsocketCommunicator


@pytest.mark.asyncio
@pytest.mark.django_db
class TestAgentChatConsumer:
    """Agent Chat WebSocket Consumer Tests

    WebSocket 연결 인증 및 권한 검증을 테스트합니다.
    """

    path = "/ws/pyhub-ai/agent/chat/"

    @pytest.mark.it("미인증 사용자는 연결 즉시, 4000 코드와 함께 웹소켓 연결이 끊어져야 합니다.")
    async def test_connect_unauthenticated(self, make_communicator):
        async with make_communicator(self.path) as communicator:
            # 서버에서는 먼저 인증 여부를 검사합니다.
            # 미인증 상황이므로, 서버에서는 클라이언트로 에러 메시지를 보내고, 웹소켓 연결을 먼저 종료합니다.

            # 모든 웹소켓 메시지 수집
            messages = []
            while True:
                try:
                    message = await communicator.receive_output(timeout=1)
                    messages.append(message)
                    if message["type"] == "websocket.close":
                        break
                    await asyncio.sleep(0.5)
                except TimeoutError:
                    break

            # 메시지 개수 확인 및 연결 종료 검증
            assert len(messages) > 0, "수신 메시지가 있어야만 합니다."

            close_message = messages[-1]
            assert close_message["type"] == "websocket.close", "마지막 메시지는 웹소켓 연결 종료 메시지여야 합니다."
            assert close_message["code"] == 4000, "커스텀 종료 코드는 4000이어야 합니다."

    @pytest.fixture
    async def auth_communicator(
        self, make_communicator, auth_credentials
    ) -> AsyncGenerator[WebsocketCommunicator, None]:
        """인증된 WebSocket communicator를 생성하는 fixture입니다.

        Args:
            make_communicator: communicator 생성 fixture
            auth_credentials: 인증 자격증명 fixture

        Returns:
            AsyncGenerator: 인증된 communicator를 생성하는 async generator
        """
        __, session_key = auth_credentials
        headers = [
            (b"cookie", f"sessionid={session_key}".encode()),
        ]
        return make_communicator(self.path, headers=headers)

    @pytest.mark.it("인증된 사용자는 유효한 세션 쿠키로 연결이 유지되어야 합니다.")
    async def test_connect_authenticated(self, auth_communicator):
        async with auth_communicator as communicator:
            # ping 메시지 전송
            await communicator.send_json_to({"type": "ping"})

            # pong 메시지 수신 확인
            response = await communicator.receive_json_from(timeout=1)
            assert response["type"] == "pong", "Response to ping message should be pong"
