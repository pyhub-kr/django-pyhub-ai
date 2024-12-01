from django.urls import path, include

from .consumers import AgentChatConsumer, DataAnalystChatConsumer

prefix = "ws/pyhub-ai/chat/"

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
    path(f"{prefix}agent/", AgentChatConsumer.as_asgi()),
    path(f"{prefix}data-analyst/", DataAnalystChatConsumer.as_asgi()),
]
