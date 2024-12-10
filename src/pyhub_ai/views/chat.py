import asyncio
from typing import AsyncGenerator, Coroutine, Literal, Optional

from django.http import HttpRequest, StreamingHttpResponse
from django.views.generic import View

from pyhub_ai.blocks import TextContentBlock
from pyhub_ai.forms import MessageForm
from pyhub_ai.mixins import ChatMixin


class ChatView(ChatMixin, View):
    form_class = MessageForm
    user_text_field_name = "user_text"
    user_images_field_name = "images"
    conversation_pk_url_kwarg = "conversation_pk"

    ready_message = "응답 생성 중 입니다. 🤖"
    chat_messages_dom_id = "chat-messages"
    template_name = "pyhub_ai/_chat_message.html"

    async def get(self, request: HttpRequest, *args, **kwargs) -> StreamingHttpResponse:
        is_accept = await self.can_accept()

        async def gen():
            # 마지막에 None 값을 추가해야만 Queue 소비가 종료됩니다.
            await self.chat_message_put(None)

        return StreamingHttpResponse(
            self.make_stream_response(gen()),
            content_type="text/event-stream; charset=utf-8",
            # 401 Unauthorized : **인증되지 않은 상태**에서 권한이 없는 리소스에 접근
            # 403 Forbidden : **인증된 상태**에서 권한이 없는 리소스에 접근
            status=200 if is_accept else 401,
        )

    async def post(self, request: HttpRequest, *args, **kwargs) -> StreamingHttpResponse:  # noqa
        is_accept = await self.can_accept()

        async def gen():
            user_text = request.POST.get(self.user_text_field_name, "").strip()
            if user_text:
                # 유저 요청을 처리하기 전에, 유저 메시지를 화면에 먼저 빠르게 렌더링합니다.
                await self.render_block(TextContentBlock(role="user", value=user_text))

            if is_accept:
                await self.form_handler(
                    data=request.POST,
                    files=request.FILES,
                    # form valid/invalid 처리 후에 Queue에 None 값을 넣어 Queue 종료를 지정
                    add_none_to_queue=True,
                )
            else:
                user = await self.get_user()
                username = user.username if user is not None else "미인증 사용자"
                await self.render_block(
                    TextContentBlock(
                        role="error",
                        value=f"{self.__class__.__module__}.{self.__class__.__name__}에서 요청을 거부했습니다. (username: {username})",
                    )
                )

        return StreamingHttpResponse(
            self.make_stream_response(gen()),
            content_type="text/event-stream; charset=utf-8",
            status=200 if is_accept else 401,
        )

    async def make_stream_response(self, coroutine_producer: Coroutine) -> AsyncGenerator[str, None]:
        producer_task = None
        try:
            queue = asyncio.Queue()

            async def receiver(_text: Optional[str]) -> None:
                await queue.put(_text)

            # ResponseQueueManager 측에서는 None 값이 수신되면 Queue에도 None 값을 넣어주도록 allow_none 인자 지정
            await self.chat_setup(receiver)

            producer_task = asyncio.create_task(coroutine_producer)

            async for text in self.make_queue_consumer(queue):
                yield text + "\n\n"  # 각 메시지를 개행문자 2개로 분리
        finally:
            # 스트림이 클라이언트에 의해 중단된 경우
            if producer_task and not producer_task.done():
                producer_task.cancel()
            await self.chat_shutdown()

    @staticmethod
    async def make_queue_consumer(queue: asyncio.Queue) -> AsyncGenerator[str, None]:
        try:
            while True:
                text = await queue.get()
                queue.task_done()
                if text is None:
                    break
                yield text
        except asyncio.CancelledError:
            pass
