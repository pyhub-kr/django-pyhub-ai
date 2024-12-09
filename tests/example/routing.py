from django.urls import path

from .consumers import LanguageTutorChatConsumer, TitanicDataAnalystChatConsumer

websocket_urlpatterns = [
    # 웹소켓을 요청하는 페이지와 주소를 동일하게 맞춰줍니다.
    # 그러면 웹소켓 연결 시 주소를 쉽게 찾을 수 있습니다.
    path("ws/example/agent/chat/<int:pk>/", LanguageTutorChatConsumer.as_asgi()),
    path("ws/example/agent/analyst/<int:pk>/", TitanicDataAnalystChatConsumer.as_asgi()),
]
