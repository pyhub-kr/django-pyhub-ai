import json
from asyncio import iscoroutinefunction
from base64 import b64encode
from dataclasses import dataclass
from typing import Any, Callable, Literal, Optional, Union
from uuid import uuid4

import pandas as pd
from django.template.loader import render_to_string
from django.utils.html import format_html
from langchain_core.messages.ai import UsageMetadata

from .utils import Mimetypes


@dataclass
class ContentBlock:
    value: Optional[str] = None
    id: Optional[str] = None  # 메시지 ID
    role: Optional[Literal["system", "user", "assistant", "tool", "event", "notice", "usage", "error", "alert"]] = None
    usage_metadata: Optional[UsageMetadata] = None  # 사용 메타데이터
    template_name: Optional[str] = None
    send_func: Optional[Callable[[str], Any]] = None

    def __post_init__(self):
        if self.id is None:
            self.id = "id_" + uuid4().hex
        self.id = self.id.replace("-", "_").strip()

    def as_markdown(self) -> Optional[str]:
        return self.value

    def get_usage_block(self) -> Optional["ContentBlock"]:
        if self.usage_metadata:
            input_tokens = self.usage_metadata["input_tokens"]
            output_tokens = self.usage_metadata["output_tokens"]
            return ContentBlock(
                role="usage",
                value=format_html(
                    """입력 토큰: {}, 출력 토큰: {}""",
                    input_tokens,
                    output_tokens,
                ),
            )
        return None


@dataclass
class EventContentBlock(ContentBlock):
    role: Literal["event"] = "event"


@dataclass
class TextContentBlock(ContentBlock):
    """텍스트 콘텐츠를 나타내는 데이터 클래스.

    Attributes:
        value (str): 텍스트 값.
    """

    value: str

    def as_markdown(self) -> str:
        return self.value


@dataclass
class CodeContentBlock(ContentBlock):
    """코드 콘텐츠를 나타내는 데이터 클래스.

    Attributes:
        value (str): 코드 텍스트 값.
        lang (Literal["python"]): 코드 언어.
    """

    value: str = ""
    lang: Literal["python"] = "python"
    role: Literal["tool"] = "tool"
    tool_name: Optional[str] = None

    def as_markdown(self) -> str:
        return f"\n```{self.lang}\n{self.value}\n```\n"


@dataclass
class DataFrameContentBlock(ContentBlock):
    """데이터프레임 콘텐츠를 나타내는 데이터 클래스.

    Attributes:
        value (Union[pd.DataFrame, pd.Series]): 데이터프레임 또는 시리즈 객체.
    """

    value: Union[pd.DataFrame, pd.Series]
    tool_name: str = "DataFrame"

    def as_markdown(self) -> str:
        if isinstance(self.value, (pd.DataFrame, pd.Series)):
            return "\n" + self.value.to_markdown() + "\n"
        else:
            return "\n" + str(self.value) + "\n"


@dataclass
class ImageDataContentBlock(ContentBlock):
    """이미지 콘텐츠를 나타내는 데이터 클래스.

    Attributes:
        value (bytes): 이미지 데이터.
    """

    value: bytes
    mimetype: Mimetypes = Mimetypes.JPEG
    tool_name: str = "image"

    def as_markdown(self) -> str:
        b64_str: str = b64encode(self.value).decode()
        return f"![{self.id}](data:{self.mimetype.value};base64,{b64_str})"


@dataclass
class ImageUrlContentBlock(ContentBlock):
    value: str

    def as_markdown(self) -> Optional[str]:
        return f"![{self.id}]({self.value})"


ContentBlockType = Union[
    TextContentBlock,
    CodeContentBlock,
    DataFrameContentBlock,
    ImageDataContentBlock,
]

MessageBlockRenderModeType = Literal[
    "append",
    "overwrite",
    "delete",
    "page-reload",
    "thinking-start",
    "thinking-end",
]


@dataclass
class MessageBlock:
    chat_messages_dom_id: str
    content_block: ContentBlock
    template_name: str
    send_func: Optional[Callable[[str], Any]] = None
    render_format: Literal["json", "htmx"] = "htmx"

    async def render(
        self,
        mode: MessageBlockRenderModeType = "overwrite",
    ) -> str:
        if self.render_format == "htmx":
            text = render_to_string(
                self.template_name,
                {
                    "chat_messages_dom_id": self.chat_messages_dom_id,
                    "content_block": self.content_block,
                    "mode": mode,
                },
            )
        elif self.render_format == "json":
            obj = {
                "id": self.content_block.id,
                "content": self.content_block.as_markdown(),
                "mode": mode,
                "role": self.content_block.role,
            }
            text = json.dumps(
                obj,
                ensure_ascii=False,
            )
        else:
            raise ValueError(f"Invalid output format: {self.render_format}")

        if self.send_func:
            if iscoroutinefunction(self.send_func):
                await self.send_func(text)
            else:
                self.send_func(text)

        return text

    async def append(self, content_block: Union[ContentBlock, str]) -> None:
        if isinstance(content_block, str):
            content_block = TextContentBlock(value=content_block)
        self.content_block = content_block
        await self.render(mode="append")

    async def update(self, content_block: Union[ContentBlock, str]) -> None:
        if isinstance(content_block, str):
            content_block = TextContentBlock(value=content_block)
        self.content_block = content_block
        await self.render(mode="overwrite")

    async def delete(self) -> None:
        await self.render(mode="delete")

    async def page_reload(self) -> None:
        await self.render(mode="page-reload")

    async def thinking_start(self) -> None:
        await self.render(mode="thinking-start")

    async def thinking_end(self) -> None:
        await self.render(mode="thinking-end")
