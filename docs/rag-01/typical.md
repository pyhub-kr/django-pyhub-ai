# 전형적인 RAG를 바닥부터 구현해보기

랭체인 등의 라이브러리를 사용하면 RAG를 손쉽게 구현할 수 있지만, 이는 단순히 API를 사용할 뿐 입니다.
RAG 과정을 바닥부터 구현하여 데이터 변환, 임베딩, 검색 등의 과정들이 어떻게 연결되는 지 직접 경험해봅시다.
이는 추후 최적화나 커스텀 기능을 구현할 때 도움이 될 것입니다.

## 사전 준비 단계

1. Load : 문서를 TXT 포맷으로 변환
    - 랭체인 타입 : `List[Document]`
2. Split : 각 문서들을 의미있는 단위로 재구성
    - 랭체인 타입 : 각 문서 내용이 재구성된 `List[Document]`
    - 문서가 너무 작으면, 하나의 내용이 끊겨 여러 문서로 쪼개져 한 문서에 충분한 정보가 담기지 못하고, 같은 내용이 여러 문서에 걸쳐 반복되기도 하고, 결국 검색 성능이 떨어집니다.
    - 문서가 너무 크면, 질문과 직접적으로 관련된 정보를 찾기가 어렵고, 프롬프트에 관련이 없는 부분까지 포함될 가능성이 높아짐.
    - 분할 전략 : 고정 길이 (문맥이 단절될 가능성 높음), 의미 기반 (문단/문장 단위로 의미적 유사도를 고려), 슬라이딩 윈도우 (문서 조각을 일부 겹치기)
3. Embed : 조각들을 임베딩
4. Store : 임베딩된 조각들을 저장
    - Vector Store에 저장

### 1단계. Load

```{code-block} python
:linenos:
:caption: 문서를 TXT 포맷으로 변환

from typing import List
from pprint import pprint
from langchain_core.documents import Document

def load() -> List[Document]:
    file_path = "빽다방.txt"
    지식: str = open(file_path, "rt", encoding="utf-8").read()
    return [
        Document(
            metadata={"source": file_path},
            page_content=지식,
        )
    ]

doc_list = load()
print(f"loaded {len(doc_list)} documents")
pprint(doc_list)
```

```{code-block} text
[Document(metadata={'source': '빽다방.txt'}, page_content='1. 아이스티샷추가(아.샷.추)\n  - SNS에서 더 유명한 꿀팁 조합 음료 :) 상콤달콤한 복숭아맛 아이스티에 진한 에스프레소 샷이 어우러져 환상조합\n  - 가격: 3800원\n\n2. 바닐라라떼(ICED)\n  - 부드러운 우유와 달콤하고 은은한 바닐라가 조화를 이루는 음료\n  - 가격: 4200원\n\n3. 사라다빵\n  - 빽다방의 대표메뉴 :) 추억의 감자 사라다빵\n  - 가격: 3900원\n\n4. 빽사이즈 아메리카노(ICED)\n  - 에스프레소 4샷이 들어가 깊고 진한 맛의 아메리카노\n  - 가격: 3500원\n\n5. 빽사이즈 원조커피(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) [주의. 564mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원\n\n6. 빽사이즈 원조커피 제로슈거(ICED)\n  - 빽다방의 BEST메뉴를 더 크게, 제로슈거로 즐겨보세요 :) [주의. 686mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원\n\n7. 빽사이즈 달콤아이스티(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) 시원한 복숭아맛 아이스티\n  - 가격: 4300원\n\n8. 빽사이즈 아이스티샷추가(ICED)\n  - SNS에서 더 유명한 꿀팁 조합 음료 :) 상콤달콤한 복숭아맛 아이스티에 진한 에스프레소 2샷이 어우러져 환상조합\n  - 가격: 4800원\n\n9. 빽사이즈 아이스티 망고추가+노란빨대\n  - SNS핫메뉴 아이스티에 망고를 한가득:)\n  - 가격: 6300원\n\n10. 빽사이즈 초코라떼(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) 진짜~완~전 진한 초코라떼\n  - 가격 : 5500원\n')]
```

### 2단계. Split

```{code-block} python
:linenos:
:caption: 각 문서들을 의미있는 단위로 재구성
:emphasize-lines: 1-11,15-16

def split(src_doc_list: List[Document]) -> List[Document]:
    new_doc_list = []
    for doc in src_doc_list:
        for new_page_content in doc.page_content.split("\n\n"):
            new_doc_list.append(
                Document(
                    metadata=doc.metadata.copy(),
                    page_content=new_page_content,
                )
            )
    return new_doc_list

doc_list = load()
print(f"loaded {len(doc_list)} documents")
doc_list = split(doc_list)
print(f"split into {len(doc_list)} documents")
# pprint(doc_list)
```

```{code-block} text
[Document(metadata={'source': '빽다방.txt'}, page_content='1. 아이스티샷추가(아.샷.추)\n  - SNS에서 더 유명한 꿀팁 조합 음료 :) 상콤달콤한 복숭아맛 아이스티에 진한 에스프레소 샷이 어우러져 환상조합\n  - 가격: 3800원'),
 Document(metadata={'source': '빽다방.txt'}, page_content='2. 바닐라라떼(ICED)\n  - 부드러운 우유와 달콤하고 은은한 바닐라가 조화를 이루는 음료\n  - 가격: 4200원'),
 Document(metadata={'source': '빽다방.txt'}, page_content='3. 사라다빵\n  - 빽다방의 대표메뉴 :) 추억의 감자 사라다빵\n  - 가격: 3900원'),
 Document(metadata={'source': '빽다방.txt'}, page_content='4. 빽사이즈 아메리카노(ICED)\n  - 에스프레소 4샷이 들어가 깊고 진한 맛의 아메리카노\n  - 가격: 3500원'),
 Document(metadata={'source': '빽다방.txt'}, page_content='5. 빽사이즈 원조커피(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) [주의. 564mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원'),
 Document(metadata={'source': '빽다방.txt'}, page_content='6. 빽사이즈 원조커피 제로슈거(ICED)\n  - 빽다방의 BEST메뉴를 더 크게, 제로슈거로 즐겨보세요 :) [주의. 686mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원'),
 Document(metadata={'source': '빽다방.txt'}, page_content='7. 빽사이즈 달콤아이스티(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) 시원한 복숭아맛 아이스티\n  - 가격: 4300원'),
 Document(metadata={'source': '빽다방.txt'}, page_content='8. 빽사이즈 아이스티샷추가(ICED)\n  - SNS에서 더 유명한 꿀팁 조합 음료 :) 상콤달콤한 복숭아맛 아이스티에 진한 에스프레소 2샷이 어우러져 환상조합\n  - 가격: 4800원'),
 Document(metadata={'source': '빽다방.txt'}, page_content='9. 빽사이즈 아이스티 망고추가+노란빨대\n  - SNS핫메뉴 아이스티에 망고를 한가득:)\n  - 가격: 6300원'),
 Document(metadata={'source': '빽다방.txt'}, page_content='10. 빽사이즈 초코라떼(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) 진짜~완~전 진한 초코라떼\n  - 가격 : 5500원\n')]
```

### 3단계. Embed

```{code-block} python
:linenos:

def embed(doc_list: List[Document]) -> List[Dict]:
    vector_store = []

    for doc in doc_list:
        text = doc.page_content
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        vector_store.append(
            {
                "text": text,
                "embedding": response.data[0].embedding,
            }
        )

    return vector_store

doc_list = load()
print(f"loaded {len(doc_list)} documents")
doc_list = split(doc_list)
print(f"split into {len(doc_list)} documents")
# pprint(doc_list)

vector_store = embed(doc_list)
print(f"created {len(vector_store)} items in vector store")
for row in vector_store:
    print(
        "{}... => {} 차원, {} ...".format(
            row["text"][:10], len(row["embedding"]), row["embedding"][:3]
        )
    )
```

```{code-block} text
loaded vector store
created 10 items in vector store
1. 아이스티샷추가... => 1536 차원, [-0.02693873643875122, -0.043540798127651215, -0.06421414762735367] ...
2. 바닐라라떼(I... => 1536 차원, [0.02490091510117054, -0.04808296635746956, -0.04629625380039215] ...
3. 사라다빵
  ... => 1536 차원, [0.027449999004602432, -0.04239306598901749, -0.008091442286968231] ...
4. 빽사이즈 아메... => 1536 차원, [-0.009449880570173264, -0.03460339829325676, -0.012358356267213821] ...
5. 빽사이즈 원조... => 1536 차원, [0.03321684151887894, 0.035661567002534866, -0.04043886810541153] ...
6. 빽사이즈 원조... => 1536 차원, [0.04160701856017113, -0.0009915598202496767, -0.037660740315914154] ...
7. 빽사이즈 달콤... => 1536 차원, [0.014812068082392216, -0.01777448132634163, -0.06847946345806122] ...
8. 빽사이즈 아이... => 1536 차원, [-0.011549889110028744, -0.02412295714020729, -0.0772319808602333] ...
9. 빽사이즈 아이... => 1536 차원, [0.009231451898813248, 0.050084274262189865, -0.03833024203777313] ...
10. 빽사이즈 초... => 1536 차원, [0.0744316577911377, 0.013424741104245186, -0.03848211094737053] ...
```

### 4단계. Store

```{code-block} python
:linenos:
:caption: list 기반으로 VectorStore 구현

class VectorStore(list):
    embedding_model = "text-embedding-3-small"

    @classmethod
    def make(cls, doc_list: List[Document]) -> "VectorStore":
        vector_store = cls()

        for doc in doc_list:
            text = doc.page_content
            response = client.embeddings.create(
                model=cls.embedding_model,
                input=text,
            )
            vector_store.append(
                {
                    "text": text,
                    "embedding": response.data[0].embedding,
                }
            )

        return vector_store

# vector_store = embed(doc_list)
vector_store = VectorStore.make(doc_list)
```

```{admonition} 현재의 VectorStore는 메모리 기반이므로, 프로세스가 종료되면 데이터가 사라집니다.
:class: tip

데이터는 변경되지 않았는 데 매번 임베딩을 수행해서 VectorStore를 생성하는 것은 비효율적입니다.
파일 혹은 데이터베이스로의 저장이 필요할텐데요.
`vector_store` 리스트 값을 pickle 혹은 json 포맷으로 저장하고, 프로세스 시작 시에 로딩토록 구현하실 수 있습니다.
```

질문과 유사한 문서를 찾아주는 `search` 메서드를 구현해봅시다. 다음 검색 단계에서 활용하겠습니다.

+ 의존 라이브러리 : `scikit-learn`

```{code-block} python
:linenos:
:emphasize-lines: 1-2,23-41

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class VectorStore(list):
    embedding_model = "text-embedding-3-small"

    @classmethod
    def make(cls, doc_list: List[Document]) -> "VectorStore":
        vector_store = cls()

        for doc in doc_list:
            text = doc.page_content
            response = client.embeddings.create(model=cls.embedding_model, input=text)
            vector_store.append(
                {
                    "text": text,
                    "embedding": response.data[0].embedding,
                }
            )

        return vector_store

    def search(self, question: str, top_k: int = 4) -> List[Document]:
        response = client.embeddings.create(
            model=self.embedding_model,
            input=question,
        )
        question_embedding = response.data[0].embedding
        embedding_list = [row["embedding"] for row in self]

        # 모든 데이터와 코사인 유사도 계산
        similarities = cosine_similarity([question_embedding], embedding_list)[0]
        # 유사도가 높은 순으로 정렬하여 top_k 개 선택
        top_indices = np.argsort(similarities)[::-1][:top_k]

        return [
            Document(
                metadata={"similarity": similarities[idx]},
                page_content=self[idx]["text"],
            )
            for idx in top_indices
        ]
```

## 검색 단계

1. Question : 유저로부터 질문 받기
2. Retrieve : 질문에 대한 정보가 저장된 Vector Store에서 질문과 유사도가 높은 문서들을 k개 찾기
3. Prompt : 질문과 찾은 문서들을 프롬프트에 포함시켜 LLM에게 요청

1, 2, 3 단계를 수행하고 즉시 유저에게 답변이 전달됩니다.


### 1단계. Question

```{code-block} python
:linenos:

question = "빽다방 카페인이 높은 음료와 가격은?"
```

### 2단계. Retrieve

```{code-block} python
:linenos:

search_doc_list = vector_store.search(question)
pprint(search_doc_list)

지식 = "\n\n".join(doc.page_content for doc in search_doc_list)
print(지식)
```

```{code-block} text
[Document(metadata={'similarity': np.float64(0.5277397661028228)}, page_content='5. 빽사이즈 원조커피(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) [주의. 564mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원'),
 Document(metadata={'similarity': np.float64(0.48501736294457715)}, page_content='6. 빽사이즈 원조커피 제로슈거(ICED)\n  - 빽다방의 BEST메뉴를 더 크게, 제로슈거로 즐겨보세요 :) [주의. 686mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원'),
 Document(metadata={'similarity': np.float64(0.44466698857735154)}, page_content='3. 사라다빵\n  - 빽다방의 대표메뉴 :) 추억의 감자 사라다빵\n  - 가격: 3900원'),
 Document(metadata={'similarity': np.float64(0.4417518412395163)}, page_content='2. 바닐라라떼(ICED)\n  - 부드러운 우유와 달콤하고 은은한 바닐라가 조화를 이루는 음료\n  - 가격: 4200원')]

 5. 빽사이즈 원조커피(ICED)
  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) [주의. 564mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]
  - 가격: 4000원

6. 빽사이즈 원조커피 제로슈거(ICED)
  - 빽다방의 BEST메뉴를 더 크게, 제로슈거로 즐겨보세요 :) [주의. 686mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]
  - 가격: 4000원

3. 사라다빵
  - 빽다방의 대표메뉴 :) 추억의 감자 사라다빵
  - 가격: 3900원

2. 바닐라라떼(ICED)
  - 부드러운 우유와 달콤하고 은은한 바닐라가 조화를 이루는 음료
  - 가격: 4200원
```

### 3단계. Prompt

```{code-block} python
:linenos:

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
print()
print("[AI]", res.choices[0].message.content)
print_prices(res.usage.prompt_tokens, res.usage.completion_tokens)
```

```{code-block} text
[AI] 빽다방에서 카페인이 높은 음료는 다음과 같습니다:

1. 빽사이즈 원조커피(ICED) - 564mg 고카페인, 가격: 4000원
2. 빽사이즈 원조커피 제로슈거(ICED) - 686mg 고카페인, 가격: 4000원

이 두 음료가 카페인이 가장 높습니다.
input: tokens 293, krw 0.0659
output: tokens 93, krw 0.083700
```

## 전체 코드

+ 의존 라이브러리 : `openai langchain scikit-learn numpy`

```{code-block} python
:linenos:

import os
import pickle
from pprint import pprint
from typing import List, Dict

from langchain_core.documents import Document
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import openai


client = openai.Client()


def load() -> List[Document]:
    file_path = "빽다방.txt"
    지식: str = open(file_path, "rt", encoding="utf-8").read()
    return [
        Document(
            metadata={"source": file_path},
            page_content=지식,
        )
    ]


def split(src_doc_list: List[Document]) -> List[Document]:
    new_doc_list = []
    for doc in src_doc_list:
        for new_page_content in doc.page_content.split("\n\n"):
            new_doc_list.append(
                Document(
                    metadata=doc.metadata.copy(),
                    page_content=new_page_content,
                )
            )
    return new_doc_list


class VectorStore(list):
    embedding_model = "text-embedding-3-small"

    @classmethod
    def make(cls, doc_list: List[Document]) -> "VectorStore":
        vector_store = cls()

        for doc in doc_list:
            text = doc.page_content
            response = client.embeddings.create(model=cls.embedding_model, input=text)
            vector_store.append(
                {
                    "text": text,
                    "embedding": response.data[0].embedding,
                }
            )

        return vector_store

    def search(self, question: str, top_k: int = 4) -> List[Document]:
        # pip install -U scikit-learn

        response = client.embeddings.create(model=self.embedding_model, input=question)
        question_embedding = response.data[0].embedding
        embedding_list = [row["embedding"] for row in self]

        # 모든 데이터와 코사인 유사도 계산
        similarities = cosine_similarity([question_embedding], embedding_list)[0]
        # 유사도가 높은 순으로 정렬하여 top_k 개 선택
        top_indices = np.argsort(similarities)[::-1][:top_k]

        return [
            Document(
                metadata={"similarity": similarities[idx]},
                page_content=self[idx]["text"],
            )
            for idx in top_indices
        ]


def print_prices(input_tokens: int, output_tokens: int) -> None:
    input_price = (input_tokens * 0.150 / 1_000_000) * 1_500
    output_price = (output_tokens * 0.600 / 1_000_000) * 1_500
    print("input: tokens {}, krw {:.4f}".format(input_tokens, input_price))
    print("output: tokens {}, krw {:4f}".format(output_tokens, output_price))


def main():
    vector_store_path = "vector_store.pickle"

    if not os.path.exists(vector_store_path):
        doc_list = load()
        print(f"loaded {len(doc_list)} documents")
        doc_list = split(doc_list)
        print(f"split into {len(doc_list)} documents")

        print("making vector store")
        # vector_store = embed(doc_list)
        vector_store = VectorStore.make(doc_list)
        with open(vector_store_path, "wb") as f:
            pickle.dump(vector_store, f)
            print("vector store saved")
    else:
        with open(vector_store_path, "rb") as f:
            vector_store = pickle.load(f)
            print("loaded vector store")

    question = "빽다방 카페인이 높은 음료와 가격은?"
    search_doc_list = vector_store.search(question)
    pprint(search_doc_list)

    지식 = "\n\n".join(doc.page_content for doc in search_doc_list)
    print(지식)

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
    print()
    print("[AI]", res.choices[0].message.content)
    print_prices(res.usage.prompt_tokens, res.usage.completion_tokens)


if __name__ == "__main__":
    main()
```
