from contextlib import asynccontextmanager
from typing import AsyncGenerator, List, Optional, Tuple
from uuid import uuid4

import pytest
from asgiref.sync import sync_to_async
from asgiref.typing import ASGIApplication
from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import BACKEND_SESSION_KEY, HASH_SESSION_KEY, SESSION_KEY
from django.contrib.sessions.backends.db import SessionStore
from django.test import AsyncClient

from pyhub_ai.routing import websocket_urlpatterns


@pytest.fixture
def agent_application() -> ASGIApplication:
    return AuthMiddlewareStack(URLRouter(websocket_urlpatterns))


@pytest.fixture
async def make_communicator(agent_application: ASGIApplication):
    @asynccontextmanager
    async def _make_communicator(
        path: str,
        auto_connect: bool = True,
        headers: Optional[List[Tuple[bytes, bytes]]] = None,
    ) -> AsyncGenerator[WebsocketCommunicator, None]:
        communicator = WebsocketCommunicator(
            application=agent_application,
            path=path,
            headers=headers,
        )
        try:
            if auto_connect:
                connected, __ = await communicator.connect()
                assert connected  # 초기 연결은 성공

            yield communicator
        finally:
            await communicator.disconnect()

    return _make_communicator


@pytest.fixture
async def auth_credentials(django_user_model) -> tuple[str, str]:
    """인증된 사용자의 자격증명을 생성합니다.

    Returns:
        tuple[str, str]: (username, session_key) 튜플을 반환합니다.
    """
    username = f"testuser_{uuid4().hex[:8]}"  # 랜덤 사용자명 생성
    user = await django_user_model.objects.acreate(username=username)

    session = SessionStore()
    session[SESSION_KEY] = str(user.pk)
    session[BACKEND_SESSION_KEY] = "django.contrib.auth.backends.ModelBackend"
    session[HASH_SESSION_KEY] = user.get_session_auth_hash()
    await sync_to_async(session.save)()

    return username, session.session_key


@pytest.fixture
def csrf_async_client() -> AsyncClient:
    """CSRF 검증이 활성화된 AsyncClient fixture"""
    return AsyncClient(enforce_csrf_checks=True)
