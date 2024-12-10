from typing import Callable, Coroutine

from django.utils.decorators import method_decorator

from pyhub_ai.decorators import acsrf_exempt
from pyhub_ai.mixins import AgentMixin

from .chat import ChatView


@method_decorator(acsrf_exempt, name="dispatch")
class AgentChatView(AgentMixin, ChatView):
    llm_system_prompt_template = "You are a helpful assistant."

    async def chat_setup(self, send_func: Callable[[str], Coroutine]) -> None:
        await super().chat_setup(send_func)

        # GET 요청에서는 기존 대화내역을 렌더링하고
        # POST 요청에서는 기존 대화내역을 렌더링하지 않고 새 내역만 렌더링합니다.
        render_previous_messages = self.request.method == "GET"
        await self.agent_setup(render_previous_messages=render_previous_messages)
