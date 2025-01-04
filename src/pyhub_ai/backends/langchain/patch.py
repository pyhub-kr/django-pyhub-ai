from typing import Any, Type

from langchain_community.chat_models import naver
from langchain_core.messages import AIMessageChunk, BaseMessageChunk

orig_convert_chunk_to_message_chunk = naver._convert_chunk_to_message_chunk


def new_convert_chunk_to_message_chunk(sse: Any, default_class: Type[BaseMessageChunk]) -> BaseMessageChunk:
    # naver 루틴에서 error 이벤트에 대한 처리가 없어, AttributeError가 발생함에 대응
    if sse.event == "error":
        return AIMessageChunk(content=f"Error: {sse.json()}")

    return orig_convert_chunk_to_message_chunk(sse, default_class)


naver._convert_chunk_to_message_chunk = new_convert_chunk_to_message_chunk
