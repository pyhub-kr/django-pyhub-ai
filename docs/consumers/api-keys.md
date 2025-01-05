# API Key 설정방법

 지원 LLM 모델은 [src/pyhub_ai/specs.py](https://github.com/pyhub-kr/django-pyhub-ai/blob/main/src/pyhub_ai/specs.py) 소스 파일을 통해 확인하실 수 있습니다.

| Provider  | Model                        | Multimodal | Tool Calling |
|-----------|------------------------------|------------|--------------|
| OpenAI    | `gpt-4o`                     | ✅          | ✅            |
| OpenAI    | `gpt-4o-mini`                | ✅          | ✅            |
| OpenAI    | `gpt-4-turbo`                | ✅          | ❌            |
| Anthropic | `claude-3-5-sonnet-20241022` | ✅          | ✅            |
| Anthropic | `claude-3-5-haiku-20241022`  | ✅          | ❌            |
| Anthropic | `claude-3-opus-20240229`     | ✅          | ✅            |
| Google    | `gemini-1.5-flash`           | ✅          | ✅            |
| Google    | `gemini-1.5-pro`             | ✅          | ✅            |
| NCP       | `HCX-DASH-001`               | ❌          | ❌            |
| NCP       | `HCX-003`                    | ❌          | ❌            |

## 환경변수를 통한 API Key 설정

API Key처럼 민감한 계정정보는 절대 소스코드에 포함시키지 않습니다. 환경변수를 통해 주입받는 것이 일반적입니다.
개발환경에서는 `.env` 파일을 통해 환경변수 설정을 주입받고, 배포환경에서는 배포환경에 맞게 환경변수를 설정해주셔야만 합니다.

## OpenAI API 설정 방법

`OPENAPI_API_KEY` 환경변수로 지정할 API Key가 1개 필요합니다.

[OpenAI 대시보드의 API Keys](https://platform.openai.com/api-keys) 페이지 "Create new secret key" 메뉴를 통해 API Key를 발급받으실 수 있습니다. 이때 API 권한 (Permissions)에 제한 (Restricted)을 거실 경우, 반드시 "Model capabilities" 권한은 `Write`로 지정해주셔야만 합니다.

API Key는 아래 우선순위 대로 적용됩니다. 

1. Consumer `get_llm_openai_api_key` 메서드 : 동적으로 Key 지정이 필요할 때
2. Consumer `llm_openai_api_key` 클래스 변수 : Consumer 마다 다른 Key 지정이 필요할 때
3. (추천) 새로운 settings 설정 `OPENAI_API_KEY` 추가 : 프로젝트 내 다른 Consumer와 Key를 공유할 때. 명시적인 설정. 환경변수 `OPENAI_API_KEY`로부터 설정을 주입받도록 합니다.

```{code-block} python
:caption: mysite/settings.py

OPENAI_API_KEY = env.str("OPENAI_API_KEY", default=None)
```

4. 환경변수 `OPENAI_API_KEY` : 프로젝트 내 다른 Consumer와 Key를 공유할 때. 3번 방법과 동일하지만 암시적인 설정입니다. 3번 방법을 추천합니다.

## Anthropic API 설정 방법

`ANTHROPIC_API_KEY` 환경변수로 지정할 API Key가 1개 필요합니다. Anthropic [API Keys](https://console.anthropic.com/settings/keys) 페이지 "Create Key" 메뉴를 통해 API Key를 발급받으실 수 있습니다. (공식문서 - [API 사용하기](https://docs.anthropic.com/ko/api/getting-started))

API Key는 아래 우선순위 대로 적용됩니다.

1. Consumer `get_llm_anthropic_api_key` 메서드 : 동적으로 Key 지정이 필요할 때
2. Consumer `llm_anthropic_api_key` 클래스 변수 : Consumer 마다 다른 Key 지정이 필요할 때
3. (추천) 새로운 settings 설정 `ANTHROPIC_API_KEY` 추가 : 프로젝트 내 다른 Consumer와 Key를 공유할 때. 명시적인 설정. 환경변수 `ANTHROPIC_API_KEY`로부터 설정을 주입받도록 합니다.

```{code-block} python
:caption: mysite/settings.py

ANTHROPIC_API_KEY = env.str("ANTHROPIC_API_KEY", default=None)
```

4. 환경변수 `ANTHROPIC_API_KEY` : 프로젝트 내 다른 Consumer와 Key를 공유할 때. 3번 방법과 동일하지만 암시적인 설정입니다. 3번 방법을 추천합니다.

## Google API 설정 방법

`GOOGLE_API_KEY` 환경변수로 지정할 API Key가 1개 필요합니다. Google [Gemini API 키 가져오기](https://ai.google.dev/gemini-api/docs/api-key?hl=ko) 페이지를 통해 API Key를 발급받으실 수 있습니다.

API Key는 아래 우선순위 대로 적용됩니다.

1. Consumer `get_llm_google_api_key` 메서드 : 동적으로 Key 지정이 필요할 때
2. Consumer `llm_google_api_key` 클래스 변수 : Consumer 마다 다른 Key 지정이 필요할 때
3. (추천) 새로운 settings 설정 `GOOGLE_API_KEY` 추가 : 프로젝트 내 다른 Consumer와 Key를 공유할 때. 명시적인 설정. 환경변수 `GOOGLE_API_KEY`로부터 설정을 주입받도록 합니다.

```{code-block} python
:caption: mysite/settings.py

GOOGLE_API_KEY = env.str("GOOGLE_API_KEY", default=None)
```

4. 환경변수 `GOOGLE_API_KEY` : 프로젝트 내 다른 Consumer와 Key를 공유할 때. 3번 방법과 동일하지만 암시적인 설정입니다. 3번 방법을 추천합니다.

## NCP Clova Studio API 설정 방법

CLOVA Studio의 [플레이그라운드](https://clovastudio.ncloud.com/playground) 페이지에서 테스트 앱을 먼저 생성하신 후에,
API Keys를 생성하실 수 있습니다.

다음 3개의 settings 설정이 필요합니다. 다른 LLM API와는 다르게 2개의 API Key가 필요하며, 테스트 앱 여부 플래그 지정도 필요합니다.

+ `NCP_SERVICE_APP` 설정
+ `NCP_APIGW_API_KEY` 설정
    1. Consumer `get_llm_ncp_apigw_api_key` 메서드 : 동적으로 Key 지정이 필요할 때
    2. Consumer `llm_ncp_apigw_api_key` 클래스 변수 : Consumer 마다 다른 Key 지정이 필요할 때
    3. (추천) 새로운 settings 설정 `NCP_APIGW_API_KEY` 추가 : 프로젝트 내 다른 Consumer와 Key를 공유할 때. 명시적인 설정.환경변수 `NCP_APIGW_API_KEY`로부터 설정을 주입받도록 합니다.
    4. 환경변수 `NCP_APIGW_API_KEY` : 프로젝트 내 다른 Consumer와 Key를 공유할 때. 3번 방법과 동일하지만 암시적인 설정입니다. 3번 방법을 추천합니다.
+ `NCP_CLOVASTUDIO_API_KEY` 설정
    1. Consumer `get_llm_ncp_clovastudio_api_key` 메서드 : 동적으로 Key 지정이 필요할 때
    2. Consumer `llm_ncp_clovastudio_api_key` 클래스 변수 : Consumer 마다 다른 Key 지정이 필요할 때
    3. (추천) 새로운 settings 설정 `NCP_CLOVASTUDIO_API_KEY` 추가 : 프로젝트 내 다른 Consumer와 Key를 공유할 때. 명시적인 설정.환경변수 `NCP_CLOVASTUDIO_API_KEY`로부터 설정을 주입받도록 합니다.
    4. 환경변수 `NCP_CLOVASTUDIO_API_KEY` : 프로젝트 내 다른 Consumer와 Key를 공유할 때. 3번 방법과 동일하지만 암시적인 설정입니다. 3번 방법을 추천합니다.

```{code-block} python
:caption: mysite/settings.py

NCP_SERVICE_APP = env.bool("NCP_SERVICE_APP", default=False)
NCP_APIGW_API_KEY = env.str("NCP_APIGW_API_KEY", default=None)
NCP_CLOVASTUDIO_API_KEY = env.str("NCP_CLOVASTUDIO_API_KEY", default=None)
```
