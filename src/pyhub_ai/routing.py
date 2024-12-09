from django.urls import path

from .consumers import AgentChatConsumer, DataAnalystChatConsumer

prefix = "ws/pyhub-ai/agent/"

websocket_urlpatterns = [
    # path(
    #     "ws/pyhub-ai/chat/",
    #     include(
    #         [
    #             path("agent/", AgentChatConsumer.as_asgi()),
    #             path("data-analyst/", DataAnalystChatConsumer.as_asgi()),
    #         ]
    #     ),
    # ),
    path(f"{prefix}chat/", AgentChatConsumer.as_asgi()),
    path(f"{prefix}analyst/", DataAnalystChatConsumer.as_asgi()),
]
