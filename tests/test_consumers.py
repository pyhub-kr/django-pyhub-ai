from typing import AsyncGenerator
import pytest

from channels.testing import WebsocketCommunicator


@pytest.mark.asyncio
@pytest.mark.django_db
class TestAgentChatConsumer:
    """Agent Chat WebSocket Consumer Tests

    WebSocket 연결 인증 및 권한 검증을 테스트합니다.
    """

    path = "/ws/pyhub-ai/chat/agent/"

    @pytest.mark.it("미인증 사용자는 연결 즉시, 4000 코드와 함께 웹소켓 연결이 끊어져야 합니다.")
    async def test_connect_unauthenticated(self, make_communicator):
        async with make_communicator(self.path) as communicator:
            # 서버에서는 먼저 인증 여부를 검사합니다.
            # 미인증 상황이므로, 서버에서는 클라이언트로 에러 메시지를 보내고, 웹소켓 연결을 먼저 종료합니다.

            error_message = await communicator.receive_output(timeout=1)
            assert error_message["type"] == "websocket.send"

            # 연결 종료 메시지 확인
            close_message = await communicator.receive_output(timeout=1)
            assert close_message["type"] == "websocket.close"
            assert close_message["code"] == 4000

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
            message = await communicator.receive_output(timeout=1)
            assert message["type"] != "websocket.close"
