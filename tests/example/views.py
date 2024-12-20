from typing import Literal

from django.contrib.auth.decorators import login_required
from django.http.response import StreamingHttpResponse
from django.shortcuts import render
from example.agents import BestsellerMakrerAgentManager
from example.forms import BestsellerMakerForm
from example.models import ChatRoom

from pyhub_ai.blocks import TextContentBlock
from pyhub_ai.decorators import alogin_required
from pyhub_ai.models import Conversation


def index(request):
    return render(request, "example/index.html")


@login_required
def chat_room(request, type: Literal["chat", "analysis"] = "chat"):
    room, __ = ChatRoom.objects.get_or_create(owner=request.user)

    if room.conversation is None:
        conv = Conversation.objects.create(user=request.user)
        room.conversation = conv
        room.save(update_fields=["conversation"])

    conversation_pk = room.conversation.pk

    agent_url = f"/example/agent/{type}/{room.pk}/{conversation_pk}/"
    connect_url = "/ws" + agent_url
    template_name = "pyhub_ai/chat_room_ws.html"

    return render(
        request,
        template_name,
        {
            "connect_url": connect_url,
        },
    )


@alogin_required
async def bestseller_maker(request):
    if request.method == "POST":
        form = BestsellerMakerForm(data=request.POST)
        if form.is_valid():
            keyword = form.cleaned_data["keyword"]

            async def stream_response():
                block = TextContentBlock(role="alert", value="생성 중 입니다. 잠시만 기다려 주세요.")
                yield block.render("example/_text_content_block.html")

                manager = await BestsellerMakrerAgentManager().agent_setup()
                try:
                    async for block in manager.think(input_query=f"keyword: {keyword}"):
                        yield block.render("example/_text_content_block.html")
                except Exception as e:
                    block = TextContentBlock(role="error", value=f"에러: {e}")
                    yield block.render("example/_text_content_block.html")
                else:
                    block = TextContentBlock(role="alert", value="생성이 완료되었습니다.")
                    yield block.render("example/_text_content_block.html")

            return StreamingHttpResponse(
                stream_response(),
                content_type="text/event-stream; charset=utf-8",
            )

    return render(request, "example/bestseller_maker.html")
