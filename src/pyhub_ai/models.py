import logging
from typing import List, Optional, Union

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.db import models
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import AddableDict

from .json import XJSONDecoder, XJSONEncoder

logger = logging.getLogger(__name__)


UserType = Union[AbstractUser, AnonymousUser]
ConversationMessageType = Union[SystemMessage, HumanMessage, AIMessage, AddableDict]


class ConversationMessageManager(models.Manager):

    async def aget_histories(
        self,
        conversation: Optional["Conversation"] = None,
        user: Optional[UserType] = None,
    ) -> List[ConversationMessageType]:
        if conversation is None:
            return []

        @sync_to_async
        def get_messages() -> List[ConversationMessageType]:
            qs = self.get_queryset().filter(
                conversation=conversation,
                user=user,
            )
            return [conversation_message.content for conversation_message in qs]

        return await get_messages()

    async def aadd_messages(
        self,
        conversation: "Conversation",
        user: Optional[UserType],
        messages: List[ConversationMessageType],
    ) -> None:
        await self.get_queryset().abulk_create(
            [
                ConversationMessage(
                    conversation=conversation,
                    user=user,
                    content=message,
                )
                for message in messages
            ]
        )


class Conversation(models.Model):
    """대화방 모델.

    Attributes:
        user (:class:`django.db.models.ForeignKey`): 대화방을 소유한 사용자. settings.AUTH_USER_MODEL을 참조하는 외래키입니다.
            `null=True`이므로 사용자 할당없이도 생성할 수 있습니다.
    """

    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def clear(self):
        """소속된 모든 ConversationMessage를 데이터베이스에서 제거합니다."""
        self.conversationmessage_set.all().delete()


class ConversationMessage(models.Model):
    """대화 메시지를 저장하는 모델.

    Attributes:
        MESSAGE_CLASS_MAP (dict): 메시지 타입별 클래스 매핑 딕셔너리 (system, human, ai)
        conversation (:class:`django.db.models.ForeignKey`): 메시지가 속한 대화방 ForeignKey
        user (:class:`django.db.models.ForeignKey`): 메시지를 작성한 사용자 ForeignKey (null 가능)
        content (:class:`django.db.models.JSONField`): 메시지 내용을 저장하는 JSONField

            * :class:`pyhub_ai.encoders.XJSONEncoder` 를 통해 JSON 인코딩
            * :class:`pyhub_ai.encoders.XJSONDecoder` 를 통해 JSON 디코딩

        objects (:class:`ConversationMessageManager`): ConversationMessageManager 커스텀 매니저
    """

    MESSAGE_CLASS_MAP = {
        "system": SystemMessage,
        "human": HumanMessage,
        "ai": AIMessage,
    }

    conversation = models.ForeignKey(
        to=Conversation,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
    )
    content = models.JSONField(
        default=dict,
        encoder=XJSONEncoder,
        decoder=XJSONDecoder,
    )
    objects = ConversationMessageManager()
