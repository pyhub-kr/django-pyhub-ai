# example 앱의 consumers.py 파일

from pyhub_ai.consumers import AgentChatConsumer, DataAnalysisChatConsumer
from pyhub_ai.specs import LLMModel
from pyhub_ai.tools import tool_with_retry
from pyhub_ai.tools.callbacks import make_tool_content_block_func
from pyhub_ai.tools.melon import search_melon_songs


class LanguageTutorChatConsumer(AgentChatConsumer):
    # get_llm_model 메서드 지원
    llm_model = LLMModel.OPENAI_GPT_4O

    llm_timeout = 5

    # get_llm_temperature 메서드 지원
    llm_temperature = 1

    # get_llm_system_prompt_template 메서드 지원
    llm_system_prompt_template = """
You are a language tutor.
{언어}로 대화를 나눕시다. 번역과 발음을 제공하지 않고 {언어}로만 답변해주세요.
"{상황}"의 상황으로 상황극을 진행합니다.
가능한한 {언어} {레벨}에 맞는 단어와 표현을 사용해주세요.
    """

    # get_llm_first_user_message_template 메서드 지원
    llm_first_user_message_template = "첫 문장으로 대화를 시작해주세요."

    # get_llm_prompt_context_data 메서드 지원
    llm_prompt_context_data = {
        "언어": "한국어",
        "상황": "친구와 식당에서 식사하는 상황",
        "레벨": "초급",
    }

    tools = [
        tool_with_retry(
            search_melon_songs,
            aget_content_block=make_tool_content_block_func(),
        ),
    ]


class TitanicDataAnalysisChatConsumer(DataAnalysisChatConsumer):
    llm_model = LLMModel.OPENAI_GPT_4O
    llm_timeout = 30
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
