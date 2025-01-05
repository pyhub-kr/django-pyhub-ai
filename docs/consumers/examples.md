# Consumer LLM 설정 예시

API Keys 설정법은 [](index) 문서를 참고해주세요.

```{code-block} python
:caption: 앱/consumers.py

from pyhub_ai.consumers import AgentChatConsumer
from pyhub_ai.specs import LLMModel

class LanguageTutorChatConsumer(AgentChatConsumer):
    llm_model = LLMModel.OPENAI_GPT_4O
    llm_temperature = 1
    llm_system_prompt_template = """
You are a language tutor.
{언어}로 대화를 나눕시다. 번역과 발음을 제공하지 않고 {언어}로만 답변해주세요.
"{상황}"의 상황으로 상황극을 진행합니다.
가능한한 {언어} {레벨}에 맞는 단어와 표현을 사용해주세요.
    """
    llm_first_user_message_template = "첫 문장으로 대화를 시작해주세요."
    llm_prompt_context_data = {
        "언어": "영어",
        "상황": "스타벅스에서 커피를 주문하는 상황",
        "레벨": "초급",
    }

    # 로그인 여부에 상관없이, 웹소켓 접속을 허용하기
    async def can_accept(self) -> bool:
        return True
```

```{code-block} python
:caption: 앱/consumers.py

from pyhub_ai.consumers import DataAnalystChatConsumer

class TitanicDataAnalystChatConsumer(DataAnalystChatConsumer):
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

    # 로그인 여부에 상관없이, 웹소켓 접속을 허용하기
    async def can_accept(self) -> bool:
        return True
```

## `llm_prompt_context_data` 지정하기

+ `llm_prompt_context_data` 클래스 변수 정의
+ `get_llm_prompt_context_data` 메서드 재정의
+ `aget_llm_prompt_context_data` 메서드 재정의
