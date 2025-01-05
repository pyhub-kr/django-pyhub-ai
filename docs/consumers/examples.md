# Consumer LLM 설정 예시

API Keys 설정법은 [](index) 문서를 참고해주세요.

## LLMMixin

### LLM 모델 지정 및 인자

클래스 변수로 지정된 설정은 고정된 설정이며, 매 요청을 처리할 때마다 동적인 설정을 적용할려면 `get_속성명` 메서드를 재정의하여 지정할 수 있습니다. 비동기 구현이 필요한 메서드는 `aget_속성명` 메서드가 제공됩니다. 장고 모델 활용이 필요하실 경우 비동기 메서드를 활용하시고, 비동기 모델/쿼리셋 API를 사용하셔야만 합니다. (예: `await 모델.objects.aget(...)`)

+ 클래스 변수 `llm_model`
    - 타입 : `LLMModel`
    - 디폴트 값 : `LLMModel.OPENAI_GPT_4O`
    - 관련 메서드 : `get_llm_model`
+ 클래스 변수 `llm_temperature`
    - 타입 : `float`
    - 디폴트 값 : `1`
    - 관련 메서드 : `get_llm_temperature`
+ 클래스 변수 `llm_max_tokens`
    - 타입 : `int`
    - 디폴트 값 : `4096`
    - 관련 메서드 : `get_llm_max_tokens`
+ 클래스 변수 `llm_timeout`
    - 타입 : `float` 이거나 `Tuple[float, float]`
    - 디폴트 값 : `5`
    - 관련 메서드 : `get_llm_timeout`

```{code-block} python
:caption: 앱/consumers.py

from pyhub_ai.consumers import AgentChatConsumer
from pyhub_ai.specs import LLMModel

class LanguageTutorChatConsumer(AgentChatConsumer):
    llm_model = LLMModel.OPENAI_GPT_4O_MINI
    llm_temperature = 0.25
    llm_max_tokens = 2048
    llm_timeout = 60
```

```{note}
지정된 LLMModel에서 지원하는 최대 max tokens값을 초과한 값으로 지정될 경우, 최대 허용값으로 강제 조정됩니다. NCP Clova Studio에서는 최대 2048 토큰을 지원하며 이 설정을 초과한 API 요청의 경우 `40003 Text too long` 에러 응답을 하며, 이 에러 응답은 `langchain-community` 라이브러리에서 처리하지 못해 `AttributeError`가 발생합니다. `django-pyhub-ai` 라이브러리에서는 이 에러 응답을 대응하며 에러 내역을 채팅 화면에 노출합니다.
```

### 시스템 프롬프트

+ `llm_system_prompt_template` : 시스템 프롬프트 문자열을 직접 지정할 경우
    - `str`, `BasePromptTemplate`, 장고 `Template` 타입들을 지원하며, 각 타입에 맞춰 적절히 렌더링합니다.
    - 별도 파일에 시스템 프롬프트 파일이 있는 경우 `llm_system_prompt_path` 설정을 활용하세요. URL 및 yaml/json/txt 포맷을 지원합니다.
+ `llm_prompt_context_data` : 시스템 프롬프트 렌더링에 필요한 input variables 값을 사전으로 지정합니다. 장고 템플릿의 `get_context_data` 메서드 역할과 동일합니다.
    - 시스템 프롬프트 뿐만 아니라, 아래의 첫 유저 메시지 생성에서도 활용됩니다. 

```{code-block} python
:caption: 앱/consumers.py

from pyhub_ai.consumers import AgentChatConsumer
from pyhub_ai.specs import LLMModel

class LanguageTutorChatConsumer(AgentChatConsumer):
    # ...

    # 문자열로 지정할 경우
    llm_system_prompt_template = "{언어}로 대화를 나눕시다. 번역/발음없이 {언어}로만 답변해주세요."

    # 정적으로 context data 지정하기
    llm_prompt_context_data = {"언어": "영어"}

    # 동적으로 값 추가가 필요할 경우 (동기 버전)
    def get_llm_prompt_context_data(self, **kwargs):
        context_data = super().get_llm_prompt_context_data()
        # context_data["..."] = "..."
        return context_data

    # 동적으로 값 추가가 필요할 경우 (비동기 버전)
    async def aget_llm_prompt_context_data(self, **kwargs):
        context_data = await super().aget_llm_prompt_context_data()
        # context_data["..."] = "..."
        return context_data
```

### 첫 유저 메시지

채팅 시작 시에 지정된 메시지를 유저 메시지로서 자동 전송할 수 있습니다.

+ `llm_first_user_message_template`
    - `str` 및 장고 `Template` 타입을 지원하며, 각 타입에 맞춰 적절히 렌더링합니다.
+ `llm_prompt_context_data` : 첫 유저 메시지 템플릿 렌더링에 필요한 input variables 값을 사전으로 지정합니다. 장고 템플릿의 `get_context_data` 메서드 역할과 동일합니다.
    - 시스템 프롬프트 렌더링에도 활용됩니다. 
    - 동기 메서드 `get_llm_prompt_context_data`와 비동기 메서드 `aget_llm_prompt_context_data`가 제공됩니다.

```{code-block} python
:caption: 앱/consumers.py

from pyhub_ai.consumers import AgentChatConsumer

class LanguageTutorChatConsumer(AgentChatConsumer):
    # ...

    llm_first_user_message_template = "첫 문장으로 대화를 시작해주세요."
    llm_prompt_context_data = {"언어": "영어"}
```

## 에이전트

+ `welcome_message_template`
    - 타입 : `str` (디폴트: `""`)
    - LLM API 호출에서는 사용되지 않고, 채팅 첫 시작 시에 유저에게만 노출할 메시지
    - `llm_prompt_context_data` 메서드를 통해서 렌더링 key 값이 자동 지정됩니다.
    - `format_html` 장고 API를 통해 `SafeString` 처리되므로 HTML 코드가 escape되지 않고 그대로 HTML로서 표현됩니다. 유저의 입력 데이터를 그대로 활용하지 마시고, 주의깊게 사용해주세요.
+ `show_initial_prompt`
    - 타입 : `bool` (디폴트: `True`)
    - 채팅 화면에 시스템 프롬프트 노출 여부 플래그
+ `verbose`
    - 타입 : `bool`
    - 랭체인 `verbose` 여부입니다. 디폴트 `None`이며 `settings.DEBUG` 값으로 자동 적용됩니다. `True`로 지정되면 랭체인 내부 메시지가 표준 출력으로 출력됩니다.
+ `tools`
    - LLM Tool Calling에 사용될 함수 리스트
    - 랭체인의 `@tool` 장식자를 적용하지 않은 파이썬 함수를 지정하시면 내부적으로 `@tool` 장식자가 자동 적용되고, 함수 description도 자동 생성됩니다. **함수의 인자 타입과 docstring은 세심히 잘 작성해주시고, 그냥 함수 리스트만 넘겨주시면 알아서 처리해줍니다.**

```{code-block} python
:caption: 앱/consumers.py

from pyhub_ai.consumers import DataAnalystChatConsumer

class TitanicDataAnalystChatConsumer(DataAnalystChatConsumer):
    # ...
    welcome_message_template = "<span class='font-bold'>타이타닉 데이터 분석</span>을 시작합니다."
```

## 데이터 분석 에이전트

+ `dataframe_path`
    - 타입 : `str`, `Path`
    - 데이터 프레임 파일 경로를 지정합니다. `.csv`, `.xls`, `.xlsx` 확장자 만을 지원하며, csv 파일은 `utf-8` 인코딩으로 처리됩니다.
    - 상대경로/절대경로/URL을 지원합니다.
+ `get_dataframe` 메서드 : 지정 경로의 데이터 파일을 로딩하여 데이터프레임 객체를 반환합니다.
    - 장고 템플릿/static 파일을 로딩할 때, 경로 지정 시에 `blog/post_list.html` 처럼 장고 앱 내의 경로를 지정하듯이, `dataframe_path` 설정에서도 `앱/data/titanic.csv` 경로에 파일이 있을 때 `dataframe_path = "data/titanic.csv"`와 같이 지정하시면, 현재 활성화된 모든 장고 앱에 대해서 상대 경로로서 `data/titanic.csv` 파일을 알아서 찾습니다.
    - 내부에서 `_dataframe` 속성으로 데이터프레임 객체를 캐싱하므로, 한 Consumer 인스턴스 내에서 `self.get_dataframe()` 메서드를 여러 번 호출하셔도 하나의 데이터프레임 인스턴스가 재사용됩니다.
+ `column_guideline`
    - 타입 : `str` 
    - 데이터프레임 각 컬럼에 대한 설명을 지정합니다.
+ `aget_llm_prompt_context_data` 메서드가 재정의되어 데이터 프레임의 첫 5개 레코드를 `dataframe_head` 키로 지정하고, `column_guideline` 값을 `column_guideline` 키로 지정합니다.

```{code-block} python
:caption: 앱/consumers.py

from pyhub_ai.consumers import DataAnalystChatConsumer

class TitanicDataAnalystChatConsumer(DataAnalystChatConsumer):
    # ...
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
```
