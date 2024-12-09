import asyncio
from functools import cached_property
from typing import (
    AsyncIterator,
    Callable,
    Coroutine,
    List,
    Literal,
    Optional,
    Type,
    Union,
)

from asgiref.sync import sync_to_async
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import File
from django.forms import Form
from django.http import QueryDict
from django.utils.datastructures import MultiValueDict

from pyhub_ai.agents.chat import ContentBlock
from pyhub_ai.blocks import (
    EventContentBlock,
    MessageBlock,
    MessageBlockRenderModeType,
    TextContentBlock,
)
from pyhub_ai.forms import MessageForm
from pyhub_ai.models import Conversation, UserType


class ChatMixin:
    form_class = MessageForm
    user_text_field_name = "user_text"
    user_images_field_name = "images"
    conversation_pk_url_kwarg = "conversation_pk"

    chat_messages_dom_id = "chat-messages"
    base64_field_name_postfix = "__base64"
    template_name = "pyhub_ai/_chat_message.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_queue_manager: Optional[ResponseQueueManager] = None

    async def chat_setup(self, send_func: Callable[[str], Coroutine]):
        self.response_queue_manager = ResponseQueueManager(send_func)
        await self.response_queue_manager.start_polling()

    async def chat_message_put(self, text: Optional[str]) -> None:
        if self.response_queue_manager:
            await self.response_queue_manager.put(text)

    async def chat_shutdown(self):
        if self.response_queue_manager:
            await self.response_queue_manager.shutdown()

    def get_template_name(self) -> str:
        return self.template_name

    def get_form_class(self) -> Type[Form]:
        return self.form_class

    @cached_property
    def query_params(self) -> QueryDict:
        if hasattr(self, "scope"):
            query_string = self.scope.get("query_string", b"")
            return QueryDict(query_string)
        elif hasattr(self, "request"):
            return self.request.GET
        raise ImproperlyConfigured("Can't query params.")

    @cached_property
    def url_route_kwargs(self):
        if hasattr(self, "scope"):
            return self.scope["url_route"]["kwargs"]
        elif hasattr(self, "kwargs"):
            return self.kwargs
        raise ImproperlyConfigured("Can't url route kwargs.")

    async def get_user(self) -> Optional[UserType]:
        if hasattr(self, "scope"):
            try:
                user = self.scope["user"]
            except KeyError:
                raise ImproperlyConfigured(
                    "scope['user']에 접근할 수 없습니다. "
                    "channels.auth.AuthMiddlewareStack이 ASGI 애플리케이션에 올바르게 구성되어 있는지 확인하세요. "
                    "\n예시: application = ProtocolTypeRouter({"
                    "\n    'websocket': AuthMiddlewareStack(URLRouter(websocket_urlpatterns))"
                    "\n})"
                )
        elif hasattr(self, "request"):
            user = self.request.user
        else:
            raise ImproperlyConfigured("Can't get user.")

        is_authenticated = await sync_to_async(lambda: user.is_authenticated)()
        if is_authenticated:
            return user
        return None

    def get_conversation_pk(self) -> Optional[str]:
        """웹소켓 요청 URL에서 추출한 대화방 식별자를 반환합니다.

        Returns:
            Optional[str]: 대화방 식별자
        """

        for candidate_key in (
            self.conversation_pk_url_kwarg,
            "conversation_pk",
            "conversation_id",
            "pk",
            "id",
        ):
            if candidate_key in self.url_route_kwargs:
                return str(self.url_route_kwargs[candidate_key])
        return None

    async def get_conversation(self) -> Optional[Conversation]:
        conversation_pk = self.get_conversation_pk()
        if conversation_pk:
            qs = Conversation.objects.filter(pk=conversation_pk)  # noqa
            return await qs.afirst()
        return None

    async def can_accept(self) -> bool:
        """연결을 수락할 수 있는지 여부를 반환합니다.

        Returns:
            bool: 연결을 수락할 수 있는 경우 True, 그렇지 않은 경우 False.
        """

        user = await self.get_user()
        if user and user.is_authenticated:
            return True
        return False

    async def form_handler(self, data: QueryDict, files: MultiValueDict, add_none_to_queue: bool = False):
        form_cls = self.get_form_class()
        form = form_cls(data=data, files=files)
        if form.is_valid():
            await self.form_valid(form)
        else:
            await self.form_invalid(form)

        if add_none_to_queue:
            await self.chat_message_put(None)

    async def form_valid(self, form: Form) -> None:
        """유효한 폼 데이터를 처리하고, 유저 입력에 대한 응답을 생성합니다.

        Args:
            form (Form): 유효한 폼 객체.
        """
        user_text = form.cleaned_data[self.user_text_field_name]
        images: List[File] = form.cleaned_data[self.user_images_field_name]

        await self.make_response(user_text=user_text, images=images)

    async def form_invalid(self, form: Form) -> None:
        """유효하지 않은 폼 데이터를 처리하고, 에러 메시지를 렌더링합니다.

        Args:
            form (Form): 유효하지 않은 폼 객체.
        """
        error_message: str = ", ".join((f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()))
        content_block = TextContentBlock(role="error", value=error_message)
        await self.render_block(content_block)

    async def think(self, input_query: str, files: Optional[List[File]] = None) -> AsyncIterator[ContentBlock]:
        """에이전트를 통해 입력 쿼리에 대해 생각하고 결과를 비동기적으로 반환합니다.

        Args:
            input_query (str): 입력 쿼리.
            files (Optional[List[File]]): 파일 목록

        Yields:
            AsyncIterator[ContentBlock]: 생성된 메시지 청크.
        """
        yield TextContentBlock("")

    @cached_property
    def render_format(self) -> Literal["json", "htmx"]:
        """JSON 요청이 아니라면 HTMX 응답"""

        # Consumer에서 요청을 처리할 경우, scope에서 헤더 확인
        if hasattr(self, "scope"):
            # 참고: htmx ws (v2.0.1) 확장을 통한 요청에서는 htmx 헤더가 하나도 없습니다.

            # WebSocket 요청인 경우 scope에서 헤더 확인
            headers = dict(self.scope.get("headers", ()))
            if headers.get("hx-request") == "true":
                return "htmx"
            if headers.get("accept") == "application/json":
                return "json"

        # Django View 에서 요청을 처리할 경우, request.headers 확인
        elif hasattr(self, "request"):
            if self.request.headers.get("HX-Request") == "true":
                return "htmx"
            if self.request.headers.get("Accept") == "application/json":
                return "json"

        return self.query_params.get("format", "htmx")

    async def render_block(
        self,
        content_block: Optional[ContentBlock] = None,
        mode: MessageBlockRenderModeType = "overwrite",
    ) -> MessageBlock:
        if content_block is None:
            content_block = EventContentBlock()

        message_block = MessageBlock(
            chat_messages_dom_id=self.chat_messages_dom_id,
            content_block=content_block,
            template_name=self.get_template_name(),
            send_func=self.chat_message_put,
            render_format=self.render_format,
        )
        await message_block.render(mode)

        return message_block

    async def make_response(
        self,
        user_text: str,
        images: Optional[List[File]] = None,
    ) -> None:
        """사용자 입력에 대한 응답을 생성하고, 메시지 타입에 맞게 렌더링합니다.

        Args:
            user_text (str): 사용자 입력 텍스트
            images (Optional[List[File]]): 첨부된 사진 파일 목록
        """

        thinking_block = await self.render_block(mode="thinking-start")

        current_message_block: Optional[MessageBlock] = None
        content_block: ContentBlock
        async for content_block in self.think(input_query=user_text, files=images):
            # 새 메시지 블록을 렌더링하거나, 기존 메시지 블록에 추가합니다.
            if current_message_block is None or content_block.id != current_message_block.content_block.id:
                current_message_block = await self.render_block(content_block)
            else:
                await current_message_block.append(content_block)

            # 사용량 블록이 있는 경우, 렌더링합니다.
            usage_block = content_block.get_usage_block()
            if usage_block:
                await self.render_block(usage_block)

        # 모든 응답 생성이 완료되면, "생각 중" 메시지를 삭제합니다.
        if thinking_block is not None:
            await thinking_block.thinking_end()


class ResponseQueueManager:
    def __init__(
        self,
        send_func: Callable[[Optional[str]], Coroutine[None, None, None]],
    ):
        self.queue = asyncio.Queue()
        self.send_func = send_func
        self.task: Optional[asyncio.Task] = None

    async def start_polling(self) -> None:
        async def polling():
            try:
                while True:
                    item: Optional[str] = await self.queue.get()
                    self.queue.task_done()

                    await self.send_func(item)
                    if item is None:
                        break
            except asyncio.CancelledError:
                # 큐를 비우고 종료
                while not self.queue.empty():
                    self.queue.get_nowait()
                    self.queue.task_done()
                raise  # 취소 시그널을 상위로 전파

        self.task = asyncio.create_task(polling())

    async def put(self, response: Union[str]) -> None:
        await self.queue.put(response)

    async def shutdown(self) -> None:
        if self.task and not self.task.done():
            await self.queue.put(None)
            await self.task
