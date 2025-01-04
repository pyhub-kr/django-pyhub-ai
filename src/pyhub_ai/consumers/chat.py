import asyncio
import sys
import traceback
from typing import Dict, Optional, Type

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.forms import Form
from django.http import QueryDict
from django.utils.datastructures import MultiValueDict

from pyhub_ai.blocks import TextContentBlock
from pyhub_ai.mixins import ChatMixin
from pyhub_ai.utils import extract_base64_files


class ChatConsumer(ChatMixin, AsyncJsonWebsocketConsumer):
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

    async def connect(self) -> None:
        """웹소켓 연결을 처리합니다.

        연결을 수락하고 환영 메시지를 렌더링합니다.
        """

        # https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent/code

        await self.chat_setup(self.send_unless_none)  # noqa

        await self.accept()

        error_message: Optional[str] = None

        if await self.can_accept():
            try:
                await self.on_accept()
            except Exception as e:
                # 에러 메시지가 없다면, 호출스택을 노출시킵니다.
                error_message = str(e)  # or ("```\n" + traceback.format_exc() + "\n```")
                if error_message:
                    error_message = "```\n" + error_message + "\n```"
                else:
                    tb = traceback.extract_tb(sys.exc_info()[2])
                    if tb:
                        last_frame = tb[-1]
                        # 전체 경로에서 site-packages 이후 경로만 추출
                        file_path = last_frame.filename
                        if "site-packages/" in file_path:
                            file_path = file_path.split("site-packages/")[-1]
                        elif "src/" in file_path:
                            file_path = file_path.split("src/")[-1]
                        error_message = (
                            "```\n" + f"Error in {file_path}, line {last_frame.lineno}: {type(e).__name__}" + "\n```"
                        )
        else:
            user = await self.get_user()
            username = user.username if user is not None else "미인증 사용자"
            error_message = f"{self.__class__.__module__}.{self.__class__.__name__}에서 웹소켓 연결을 거부했습니다. (username: {username})"

        if error_message is not None:
            await self.render_block(
                TextContentBlock(
                    role="error",
                    value=error_message,
                )
            )
            # 즉시 close하면 websocket send 전에 닫히므로, close를 1초 지연시킵니다.
            await asyncio.sleep(1)
            await self.close(code=4000)

    async def send_unless_none(self, text: str) -> None:
        if text is not None:
            await self.send(text)

    async def on_accept(self) -> None:
        """연결 수락 후 추가 작업을 처리합니다."""
        pass

    async def disconnect(self, close_code: int) -> None:
        """웹소켓 연결을 종료합니다.

        Args:
            close_code (int): 연결 종료 코드.
        """
        await self.chat_shutdown()
        await self.on_disconnect(close_code)

    async def on_disconnect(self, close_code: int) -> None:
        """연결 종료 후 추가 작업을 처리합니다.

        Args:
            close_code (int): 연결 종료 코드.
        """
        pass

    async def receive_json(self, data: Dict, **kwargs):
        """JSON 형식의 메시지를 수신합니다.

        Args:
            data (Dict): 요청 데이터를 담고 있는 딕셔너리.
            **kwargs: 추가 인자.
        """

        if data.get("type") == "ping":
            await self.send_json({"type": "pong"})
        else:
            user_text = data.get(self.user_text_field_name, "").strip()
            if user_text:
                # 유저 요청을 처리하기 전에, 유저 메시지를 화면에 먼저 빠르게 렌더링합니다.
                await self.render_block(TextContentBlock(role="user", value=user_text))

            files: MultiValueDict = extract_base64_files(data, self.base64_field_name_postfix)

            query_dict = QueryDict(mutable=True)
            query_dict.update(data)

            await self.form_handler(data=query_dict, files=files)
