import logging

from pyhub_ai.mixins import AgentMixin

from .chat import ChatConsumer

logger = logging.getLogger(__name__)


class AgentChatConsumer(AgentMixin, ChatConsumer):

    # async def can_accept(self) -> bool:
    #     return True

    async def on_accept(self) -> None:
        await super().on_accept()
        await self.agent_setup()
