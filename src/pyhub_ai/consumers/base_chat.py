from typing import Dict, List, Literal, Optional, AsyncIterator, Type

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.files.base import File
from django.forms import Form
from django.http import QueryDict
from django.utils.datastructures import MultiValueDict
from django.utils.html import format_html
from django.utils.safestring import SafeString

from ..agents.chat import ContentBlock
from ..blocks import (
    MessageBlock,
    TextContentBlock,
    MessageBlockRenderModeType,
    VoidContentBlock,
)
from ..forms import MessageForm
from ..models import Conversation, UserType
from ..utils import extract_base64_files


class BaseChatConsumer(AsyncJsonWebsocketConsumer):
    """기본 채팅 컨슈머 클래스

    Attributes:
        form_class (Type[Form]): 폼 클래스.
        user_text_field_name (str): 사용자 텍스트 필드 이름.
        user_images_field_name (str): 사용자 이미지 필드 이름.
        ready_message (str): LLM 에이전트가 응답을 준비 중임을 알리는 준비 메시지.
        chat_messages_dom_id (str): 채팅 메시지 DOM ID.
        base64_field_name_postfix (str): base64 필드 이름 접미사.
        template_name (str): 템플릿 이름.
    """

    form_class = MessageForm
    user_text_field_name = "user_text"
    user_images_field_name = "images"
    conversation_pk_url_kwarg = "conversation_pk"

    ready_message = "응답 생성 중 입니다. 🤖"
    assistant_image_url = None
    chat_messages_dom_id = "chat-messages"
    base64_field_name_postfix = "__base64"
    template_name = "pyhub_ai/_chat_message.html"

    output_format: Literal["json", "htmx"] = "htmx"

    async def can_accept(self) -> bool:
        """연결을 수락할 수 있는지 여부를 반환합니다.

        Returns:
            bool: 연결을 수락할 수 있는 경우 True, 그렇지 않은 경우 False.
        """
        return True

    async def connect(self) -> None:
        """웹소켓 연결을 처리합니다.

        연결을 수락하고 환영 메시지를 렌더링합니다.
        """

        # https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent/code

        await self.accept()

        if not await self.can_accept():
            user = self.scope["user"]
            username = user.username if user.is_authenticated else "미인증 사용자"
            await self.render_block(
                TextContentBlock(
                    role="error",
                    value=f"{self.__class__.__module__}.{self.__class__.__name__}에서 웹소켓 연결을 거부했습니다. (username: {username})",
                )
            )
            await self.close(code=4000)
        else:
            await self.on_accept()

    async def on_accept(self) -> None:
        """연결 수락 후 추가 작업을 처리합니다."""
        pass

    async def disconnect(self, close_code: int) -> None:
        """웹소켓 연결을 종료합니다.

        Args:
            close_code (int): 연결 종료 코드.
        """
        await self.on_disconnect(close_code)

    async def on_disconnect(self, close_code: int) -> None:
        """연결 종료 후 추가 작업을 처리합니다.

        Args:
            close_code (int): 연결 종료 코드.
        """
        pass

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

    async def receive_json(self, request_dict: Dict, **kwargs):
        """JSON 형식의 메시지를 수신합니다.

        Args:
            request_dict (Dict): 요청 데이터를 담고 있는 딕셔너리.
            **kwargs: 추가 인자.
        """
        user_text = request_dict.get("user_text", "")
        if user_text:
            # 유저 요청을 처리하기 전에, 유저 메시지를 화면에 먼저 빠르게 렌더링합니다.
            content_block = TextContentBlock(role="user", value=user_text)
            await self.render_block(content_block)

        files: MultiValueDict = extract_base64_files(request_dict, self.base64_field_name_postfix)
        form_cls = self.get_form_class()
        form = form_cls(data=request_dict, files=files)
        if form.is_valid():
            await self.form_valid(form)
        else:
            await self.form_invalid(form)

    def get_conversation_pk(self) -> Optional[str]:
        """웹소켓 요청 URL에서 추출한 대화방 식별자를 반환합니다.

        Returns:
            Optional[str]: 대화방 식별자
        """

        kwargs = self.scope["url_route"]["kwargs"]

        for candidate_key in (
            self.conversation_pk_url_kwarg,
            "conversation_pk",
            "conversation_id",
            "pk",
            "id",
        ):
            if candidate_key in kwargs:
                return str(kwargs[candidate_key])
        return None

    async def get_conversation(self) -> Optional[Conversation]:
        conversation_pk = self.get_conversation_pk()
        if conversation_pk:
            qs = Conversation.objects.filter(pk=conversation_pk)
            return await qs.afirst()
        return None

    async def get_user(self) -> Optional[UserType]:
        try:
            user = self.scope["user"]
            if user and user.is_authenticated:
                return user
        except KeyError:
            raise RuntimeError(
                "scope['user']에 접근할 수 없습니다. "
                "channels.auth.AuthMiddlewareStack이 ASGI 애플리케이션에 "
                "올바르게 구성되어 있는지 확인하세요. "
                "\n예시: application = ProtocolTypeRouter({"
                "\n    'websocket': AuthMiddlewareStack(URLRouter(websocket_urlpatterns))"
                "\n})"
            )
        return None

    async def think(
        self,
        input_query: str,
        files: Optional[List[File]] = None,
    ) -> AsyncIterator[ContentBlock]:
        """에이전트를 통해 입력 쿼리에 대해 생각하고 결과를 비동기적으로 반환합니다.

        Args:
            input_query (str): 입력 쿼리.
            files (Optional[List[File]]): 파일 목록

        Yields:
            AsyncIterator[ContentBlock]: 생성된 메시지 청크.
        """
        yield TextContentBlock("")

    def get_output_format(self) -> Literal["json", "htmx"]:
        # 캐시된 값이 있으면 반환
        if not hasattr(self, "_output_format_cache"):
            query_string = self.scope.get("query_string", b"")
            query_params = QueryDict(query_string)
            fmt = query_params.get("format", None)
            # 캐시에 저장
            self._output_format_cache = fmt if fmt is not None else self.output_format

        return self._output_format_cache

    async def render_block(
        self,
        content_block: Optional[ContentBlock] = None,
        mode: MessageBlockRenderModeType = "overwrite",
    ) -> MessageBlock:
        output_format = self.get_output_format()

        if content_block is None:
            content_block = VoidContentBlock()

        message_block = MessageBlock(
            chat_messages_dom_id=self.chat_messages_dom_id,
            content_block=content_block,
            template_name=self.get_template_name(),
            send_func=self.send,
            output_format=output_format,
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

    def get_ready_message(self) -> SafeString:
        return format_html(self.ready_message)

    def get_template_name(self) -> str:
        return self.template_name

    def get_form_class(self) -> Type[Form]:
        return self.form_class
