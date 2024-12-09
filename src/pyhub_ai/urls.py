from django.urls import path

from .views import AgentChatView

app_name = "pyhub_ai"

urlpatterns = [
    path(f"agent/chat/", AgentChatView.as_view(), name="agent-chat"),
]
