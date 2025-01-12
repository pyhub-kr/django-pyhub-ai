# 한 번에 지식 보강

## OpenAI API 가격 계산

[OpenAI API 가격 계산](https://openai.com/api/pricing/) 문서를 참고했습니다.

+ gpt-4o-mini
    - $0.150 / 1M input tokens
    - $0.600 / 1M output tokens

```{code-block} python
:linenos:

def print_prices(input_tokens: int, output_tokens: int) -> None:
    input_price = (input_tokens * 0.150 / 1_000_000) * 1_500
    output_price = (output_tokens * 0.600 / 1_000_000) * 1_500
    print("input: tokens {}, krw {:.4f}".format(input_tokens, input_price))
    print("output: tokens {}, krw {:4f}".format(output_tokens, output_price))
```

## OpenAI LLM에게 그냥 물어봅니다.

LLM이 가지고 있는 지식에 기반해서 답변합니다.

```{code-block} python
:linenos:

import openai

# 라이브러리 : pip install -U openai
# 환경변수 : OPENAI_API_KEY

client = openai.Client()

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

```{code-block} text
죄송하지만, 빽다방의 특정 음료와 가격에 대한 정보는 제공할 수 없습니다. 최신 메뉴와 가격은 빽다방 공식 웹사이트나 매장에서 확인하시는 것이 좋습니다.
input: tokens 39, krw 0.0088
output: tokens 46, krw 0.041400
```

## 지식을 전달하고 물어봅시다.

지식의 양의 Context Window 제한을 넘어서지 않는다면, 지식을 전달하고 물어볼 수 있습니다.

+ 지식 : [빽다방.txt](./빽다방.txt)

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

```{code-block} text
빽다방에서 카페인이 높은 음료는 다음과 같습니다:

1. **빽사이즈 원조커피(ICED)** - 가격: 4000원 (564mg 고카페인)
2. **빽사이즈 원조커피 제로슈거(ICED)** - 가격: 4000원 (686mg 고카페인)

이 두 음료가 카페인이 높습니다.
input: tokens 661, krw 0.1487
output: tokens 92, krw 0.082800
```
