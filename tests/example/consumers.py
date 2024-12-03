# example 앱의 consumers.py 파일

from pyhub_ai.consumers import AgentChatConsumer
from pyhub_ai.specs import LLMModel


class LanguageTutorChatConsumer(AgentChatConsumer):
    # get_llm_model 메서드 지원
    llm_model = LLMModel.OPENAI_GPT_4O

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
