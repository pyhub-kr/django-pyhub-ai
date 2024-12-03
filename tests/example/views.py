from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def index(request):
    return render(request, "example/index.html")


@login_required
def chat(request, pk: int):
    ws_url = "/ws" + request.path
    return render(
        request,
        "pyhub_ai/chat_room_ws.html",
        {
            "ws_url": ws_url,
        },
    )
