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
    """대화방"""

    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)


class ConversationMessage(models.Model):
    """메시지"""

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
