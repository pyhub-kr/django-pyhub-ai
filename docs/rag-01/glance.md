# 대화 시작 시에 한 번에 모든 지식을 제공하기

## OpenAI API 비용 계산 함수 구현

시작하기에 앞서, 사용된 입출력 토큰수에 기반해서 비용을 계산하는 함수를 작성하겠습니다.
각 LLM 응답마다 입출력 토큰 수를 알 수 있는 데요.
토큰 수만 봐서는 비용을 가늠하기 어렵기 때문입니다.
[OpenAI API 가격 계산](https://openai.com/api/pricing/) 문서를 참고했습니다.
gpt-4o-mini 모델 기준으로 입력은 100만 토큰 당 $0.15, 출력은 100만 토큰 당 $0.6 입니다.

```{code-block} python
:linenos:
:caption: 비용 계산 함수 : `oneshot.py`

def print_prices(input_tokens: int, output_tokens: int) -> None:
    input_price = (input_tokens * 0.150 / 1_000_000) * 1_500
    output_price = (output_tokens * 0.600 / 1_000_000) * 1_500
    print("input: tokens {}, krw {:.4f}".format(input_tokens, input_price))
    print("output: tokens {}, krw {:4f}".format(output_tokens, output_price))
```

## OpenAI API Key를 준비해주세요.

OpenAI API Key가 없으신 분은 [](../quickstart/first-chat-bot) 튜토리얼의 "OpenAI API Key 얻기" 섹션을 참고해서 구해주세요.

원하는 폴더 경로에 `.env` 파일을 생성해서 API Key를 저장해주시고,

```{code-block} text
:linenos:
:caption: `.env` 파일 생성

OPENAI_API_KEY=sk-...
```

`django-environ` 라이브러리를 통해 `.env` 파일을 환경변수로 로딩토록 하겠습니다.

```{code-block} shell
:linenos:

pip install -U django-environ
```

## OpenAI LLM에게 그냥 물어봅니다.

`openai` 라이브러리를 설치합니다.

```{code-block} shell
:linenos:

pip install -U openai
```

시스템 프롬프트로는 "넌 AI Assistant. 모르는 건 모른다고 대답." 이라고 지정하고,
별도의 지식 제공없이 "빽다방 카페인이 높은 음료와 가격은?" 이라고 물어보겠습니다.

```{code-block} python
:linenos:
:caption: 비용 계산 함수 : `oneshot.py`

import openai
from environ import Env

env = Env()
env.read_env()  # .env 파일을 환경변수로서 로딩


def print_prices(input_tokens: int, output_tokens: int) -> None:
    input_price = (input_tokens * 0.150 / 1_000_000) * 1_500
    output_price = (output_tokens * 0.600 / 1_000_000) * 1_500
    print("input: tokens {}, krw {:.4f}".format(input_tokens, input_price))
    print("output: tokens {}, krw {:4f}".format(output_tokens, output_price))


client = openai.Client()  # OPENAI_API_KEY 환경변수를 디폴트로 참조

res = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "넌 AI Assistant. 모르는 건 모른다고 대답.",
        },
        {
            "role": "user",
            "content": "빽다방 카페인이 높은 음료와 가격은?",
        },
    ],
    model="gpt-4o-mini",
    temperature=0,
)
print(res.choices[0].message.content)
print_prices(res.usage.prompt_tokens, res.usage.completion_tokens)
```

위 코드를 실행하고 그 응답을 받아보면 이렇게 빽다방 정보가 없다고 대답하는 것을 확인할 수 있습니다.
이 응답을 받기 위해 사용된 비용은 총 `0.0502`원입니다.

```{code-block} text
죄송하지만, 빽다방의 특정 음료와 가격에 대한 정보는 제공할 수 없습니다. 최신 메뉴와 가격은 빽다방 공식 웹사이트나 매장에서 확인하시는 것이 좋습니다.
input: tokens 39, krw 0.0088
output: tokens 46, krw 0.041400
```

## 지식을 전달하고 물어봅시다.

이제 빽다방 관련된 지식을 전달하고 물어봅시다.
지식의 양의 Context Window 제한을 넘어서지 않는다면, 대화 처음에 모든 지식을 전달하고 질문을 이어나갈 수 있습니다.

지식 파일은  [빽다방.txt](./빽다방.txt) 이며, 빽다방 메뉴 10개에 대한 지식을 담고 있습니다.

LLM에게 질문하기 전에 전체 지식을 로딩하고, 시스템 프롬프트에 추가하고 질문을 합니다.

```{code-block} python
:linenos:
:emphasize-lines: 5,11

import openai

client = openai.Client()

지식 = open("빽다방.txt", "rt", encoding="utf-8").read()

res = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": f"넌 AI Assistant. 모르는 건 모른다고 대답.\n\n[[빽다방 메뉴 정보]]\n{지식}",
        },
        {
            "role": "user",
            "content": "빽다방 카페인이 높은 음료와 가격은?",
        },
    ],
    model="gpt-4o-mini",
    temperature=0,
)
print(res.choices[0].message.content)
print_prices(res.usage.prompt_tokens, res.usage.completion_tokens)
```

위 코드를 실행하고 그 응답을 받아보면 이렇게 빽다방 정보가 정확히 있음을 확인할 수 있습니다.
이 응답을 받기 위해 사용된 비용은 총 `0.2315`원입니다.

```{code-block} text
빽다방에서 카페인이 높은 음료는 다음과 같습니다:

1. **빽사이즈 원조커피(ICED)** - 가격: 4000원 (564mg 고카페인)
2. **빽사이즈 원조커피 제로슈거(ICED)** - 가격: 4000원 (686mg 고카페인)

이 두 음료가 카페인이 높습니다.
input: tokens 661, krw 0.1487
output: tokens 92, krw 0.082800
```
