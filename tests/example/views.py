from typing import Literal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from pyhub_ai.models import Conversation


def index(request):
    return render(request, "example/index.html")


@login_required
def chat_room(request, type: Literal["chat", "analysis"] = "chat"):
    conv = Conversation.objects.filter(user=request.user).first()
    if conv is None:
        conv = Conversation.objects.create(user=request.user)

    agent_url = f"/example/agent/{type}/{conv.pk}/"
    connect_url = "/ws" + agent_url
    template_name = "pyhub_ai/chat_room_ws.html"

    return render(
        request,
        template_name,
        {
            "connect_url": connect_url,
        },
    )
