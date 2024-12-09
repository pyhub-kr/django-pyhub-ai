from typing import Literal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from pyhub_ai.specs import LLMModel
from pyhub_ai.views import AgentChatView
from pyhub_ai.views.data_analyst import DataAnalystChatView


def index(request):
    return render(request, "example/index.html")


@login_required
def chat_room(request, pk: int, type: Literal["chat", "analyst"] = "chat"):
    is_ws = request.GET.get("protocol", "ws") == "ws"

    agent_url = f"/example/agent/{type}/{pk}/"

    if is_ws:
        connect_url = "/ws" + agent_url
        template_name = "pyhub_ai/chat_room_ws.html"
    else:
        connect_url = agent_url
        template_name = "pyhub_ai/chat_room_sse.html"

    return render(
        request,
        template_name,
        {
            "connect_url": connect_url,
        },
    )


class LanguageTutorChatView(AgentChatView):
    llm_model = LLMModel.OPENAI_GPT_4O
    llm_temperature = 1
    llm_system_prompt_template = """
You are a language tutor.
{언어}로 대화를 나눕시다. 번역과 발음을 제공하지 않고 {언어}로만 답변해주세요.
"{상황}"의 상황으로 상황극을 진행합니다.
가능한한 {언어} {레벨}에 맞는 단어와 표현을 사용해주세요.
    """

    llm_first_user_message_template = "첫 문장으로 대화를 시작하세요."

    llm_prompt_context_data = {
        "언어": "한국어",
        "상황": "친구와 식당에서 식사하는 상황",
        "레벨": "초급",
    }


class TitanicDataAnalystChatView(DataAnalystChatView):
    llm_model = LLMModel.OPENAI_GPT_4O
    llm_temperature = 0
    llm_system_prompt_path = "prompts/data-analyst-v02-en.yaml"
    dataframe_path = "data/titanic.csv"
    column_guideline = """
PassengerId: 승객 번호
Survived: 생존 여부 (0: 사망, 1: 생존)
Pclass: 승객 클래스 (1: 1등석, 2: 2등석, 3: 3등석)
Name: 이름
Sex: 성별
Age: 나이
SibSp: 형제 또는 배우자 수
    """

    welcome_message_template = "<span class='font-bold'>타이타닉 데이터 분석</span>을 시작합니다."
