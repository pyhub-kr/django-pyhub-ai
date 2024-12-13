# django-pyhub-ai

> **Note**: 이 라이브러리는 현재 베타버전입니다. 기능이 변경될 수 있으며, 피드백을 환영합니다.

[django-pyhub-ai 튜토리얼](https://django-pyhub-ai.readthedocs.io)을 참고하여, 빠르게 장고 기반의 LLM 에이전트 챗봇 서비스를 구축해보세요.

장고의 핵심 철학 중 DRY(Don't Repeat Yourself) 철학을 기반으로 반복적이고 번거로운 작업을 제거하고, 효율적인 에이전트 기반 채팅 서비스를 손쉽게 구축할 수 있도록 돕는 라이브러리입니다.

이 라이브러리는 Django 프로젝트에 자연스럽게 통합되며, OpenAI API와 같은 최신 AI 기술을 활용한 기능들을 간단하게 구현할 수 있는 도구들을 하려 합니다.
복잡한 설정이나 반복적인 코드를 작성할 필요 없이, django-pyhub-ai를 통해 에이전트 채팅 서비스 개발을 더욱 간편하고 직관적으로 만들어보세요.

<p float="left">
  <img src="./docs/assets/screenshot-01.gif" width="49%" />
  <img src="./docs/assets/screenshot-02.gif" width="49%" />
</p>

## 주요 특징

django-pyhub-ai와 함께라면 개발자는 에이전트 챗봇 개발에 있어서 비효율적인 반복 작업에서 벗어나 비즈니스 로직에 집중할 수 있습니다.

- **DRY 철학 준수**: 반복적인 코드 작성 없이 간결한 서비스 구축 가능
- **빠른 통합**: Django 프레임워크와 원활한 통합 지원
- **유연한 API 활용**: OpenAI API 및 기타 AI 서비스와 쉽게 연동
- **구성 요소 제공**: 에이전트 정의, 메시지 처리, 대화 흐름 관리 등 필수 기능 내장
- **토큰 추적**: input/output 토큰 수를 실시간으로 추적하여 채팅 화면에 표시
- **메시지 관리**: 모든 채팅 메시지를 자동으로 저장하고 관리
- **Tools 통합**: 외부 Tools 호출 및 실행 결과를 자동으로 저장하고 추적
- **멀티모달 지원**: 
  - 다중 이미지 업로드를 위한 직관적인 위젯 제공
  - 이미지 기반 대화를 위한 멀티모달 요청 처리 지원
  - 이미지 분석 및 관련 대화 컨텍스트 자동 관리

## 지원 모델

현재 다음의 LLM을 지원합니다.

- OpenAI gpt-4o
- OpenAI gpt-4o-mini
- OpenAI gpt-4o-turbo
- Anthropic claude-3-5-sonnet-20241022
- Anthropic claude-3-5-haiku-20241022
- Anthropic claude-3-opus-20240229
- Google gemini-1.5-flash
- Google gemini-1.5-pro

> **Note**: 현재는 위 모델들만 지원하고 있으며, 다양한 AI 모델들을 순차적으로 추가하고 있습니다. 지속적인 업데이트를 통해 더 많은 선택지를 제공하도록 하겠습니다.

## 지원 Consumers

+ `AgentChatConsumer`: 대화형 에이전트 지원
  - 동적 시스템 프롬프트, 초기 유저 메시지 지원
  - 멀티모달 입력 지원 (이미지 다중 업로드)
  - 토큰 사용량 실시간 추적
  - 대화 이력 자동 저장 지원

+ `DataAnalystChatConsumer` : 데이터 분석 특화 에이전트 지원
  - Pandas 코드 자동 생성 및 실행 지원
  - Pandas/Matplotlib/Seaborn 기반으로 차트 및 그래프 생성 지원

### Language Tutor Chat Consumer 예제

웹소켓 연결을 통해 유저 텍스트 및 이미지 입력을 받아, 언어 강사 에이전트를 통해 대화를 진행할 수 있습니다.

`AgentChatConsumer`를 상속받아 쉽게 구현할 수 있습니다.
  - `llm_model`: LLM 모델 지정
  - `llm_temperature`: LLM 온도 지정
  - `llm_system_prompt_template`: 시스템 프롬프트 템플릿 지정
  - `llm_first_user_message_template`: 초기 유저 메시지 템플릿 지정
  - `llm_prompt_context_data`: 동적 시스템 프롬프트에 사용할 컨텍스트 데이터 지정

아래 코드 만으로 언어 강사 에이전트 구현은 끝납니다. 각 설정들은 `get_속성명` 메서드를 재정의하여 동적으로 지정하실 수도 있습니다.

[example 앱의 consumers.py 파일](./tests/example/consumers.py)

```python
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
        "언어": "한국어",
        "상황": "친구와 식당에서 식사하는 상황",
        "레벨": "초급",
    }
```

[example 앱의 routing.py 파일](./tests/example/routing.py)

```python
# example/routing.py
from django.urls import path
from .consumers import LanguageTutorChatConsumer

websocket_urlpatterns = [
    # 웹소켓을 요청하는 페이지와 주소를 동일하게 맞춰줍니다.
    # 그러면 웹소켓 연결 시 주소를 쉽게 찾을 수 있습니다.
    path("ws/example/chat/<int:pk>/", LanguageTutorChatConsumer.as_asgi()),
]
```

HTMX 응답과 JSON 응답을 지원합니다.

+ HTMX 응답 요청 (디폴트)
  - [`pyhub_ai/_chat_message.html`](src/pyhub_ai/templates/pyhub_ai/_chat_message.html) 템플릿을 사용합니다.
  - Consumer에서 `template_name` 속성이나 `get_template_name` 메서드를 재정의하여, 응답 스타일을 바꾸실 수 있습니다.
+ JSON 응답 요청
  - 웹소켓 연결 주소 끝에 `?format=json` 파라미터를 붙여주세요.
  - 리액트 등의 프론트엔드 프레임워크와 연동하기 좋습니다.

### Language Tutor Chat Consumer 예제

Consumer에서는 유저 입력 만을 처리할 뿐 UI 렌더링은 아래 예제와 같이 페이지 뷰에서 처리합니다.
HTMX 기반으로 구현된 `page_ai/chat_room_ws.html` 템플릿을 제공해드리구요.
`ws_url` 변수를 통해 웹소켓 연결 주소를 지정하시면 페이지 구현 끝입니다.

[example 앱의 views.py 파일](./tests/example/views.py)

```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def chat(request, pk: int):
    ws_url = "/ws" + request.path
    return render(
        request,
        "pyhub_ai/chat_room_ws.html",
        {
            "ws_url": ws_url,
        },
    )
```

[example 앱의 urls.py 파일](./tests/example/urls.py)

```python
from django.urls import path
from . import views

urlpatterns = [
    path("chat/<int:pk>/", views.chat, name="chat"),
]
```

### 동작 화면

설정에 가까운 코드로 이렇게 손쉽게 에이전트 챗봇을 구현할 수 있습니다.

![screenshot 01](./docs/assets/screenshot-01.gif)

## 기본 설정

[example 프로젝트](./tests/)를 참고하여 설정해보세요.

+ 라이브러리 설치: `pip install django-pyhub-ai`
+ 프로젝트 ASGI 설정
+ 프로젝트 `settings.INSTALLED_APPS`에 다음 3개 앱 추가
  - `daphne`: `INSTALLED_APPS` 리스트 처음에 추가해주셔야만, 장고 기본 `runserver` 명령을 재정의하여 ASGI 개발서버로 구동됩니다.
  - `pyhub_ai`: 본 라이브러리
  - `django_cotton`: `django-cotton` 컴포넌트를 사용하므로, 꼭 추가해주세요.

## License

본 프로젝트는 [Apache License 2.0](LICENSE) 라이선스를 따릅니다.

문의 : help@pyhub.kr
