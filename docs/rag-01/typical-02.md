# #02. 지식 준비 단계

```{figure} ./assets/typical-indexing.png
:alt: (RAG) Indexing

출처 : [랭체인 공식 튜토리얼: RAG 애플리케이션 구축하기](https://python.langchain.com/docs/tutorials/rag/)
```

1. Load : 문서를 파이썬 객체로 변환
2. Split : 각 문서들을 의미있는 단위로 재구성
3. Embed : 각 문서들을 숫자(임베딩 데이터)로 변환하여, 질문과 유사도를 계산할 준비
    - 질문과 관련된 문서를 찾기 위해, 질문과 유사도를 계산하는 방법은 현재 RAG에서 많이 사용되는 방법이며, 향후 다른 방법으로 대체될 수도 있습니다.
4. Store : 유사도 데이터를 디스크에 저장하여, 계속 사용할 수 있도록 준비
    - 문서 내용이 바뀌면, 임베딩 데이터도 매번 재생성해야 합니다.

## 1단계. Load - PDF/TXT/HTML 지식들을 일관된 파이썬 객체로 변환

반환 타입 : `List[Document]`

랭체인에서는 다양한 포맷의 파일들에 대해서 일관된 인터페이스로 파이썬 객체로 변환하는 기능을 제공해줍니다. 이를 `Document Loader`라고 합니다.

```{admonition} 랭체인 공식문서 [문서 로더](https://python.langchain.com/docs/how_to/#document-loaders)
:class: tip

+ [PDF](https://python.langchain.com/docs/how_to/document_loader_pdf/)
+ [웹페이지](https://python.langchain.com/docs/how_to/document_loader_web/)
+ [CSV](https://python.langchain.com/docs/how_to/document_loader_csv/)
+ [로컬 파일](https://python.langchain.com/docs/how_to/document_loader_directory/)
+ [HTML 데이터](https://python.langchain.com/docs/how_to/document_loader_html/)
+ [JSON 데이터](https://python.langchain.com/docs/how_to/document_loader_json/)
+ [마크다운 데이터](https://python.langchain.com/docs/how_to/document_loader_markdown/)
+ [마이크로소프트 오피스 데이터](https://python.langchain.com/docs/how_to/document_loader_office_file/)
+ [커스텀 문서 로더](https://python.langchain.com/docs/how_to/document_loader_custom/)
```

[빽다방.txt](./빽다방.txt) 파일을 문서로 변환하는 코드를 2가지 버전으로 구현했습니다.

`Load` 단계에서는 문서 포맷에 맞는 라이브러리를 사용하여, 문서를 열고 메타데이터와 내용을 읽어서 텍스트로 변환하신 후에, `metadata` 사전에는 각종 정보를 담고, `page_content` 문자열에 문서 텍스트를 담아서 반환합니다.

+ `metadata` 사전 값은 프롬프트에 문자열로서 전달됩니다.
    - 그러니 어떤 `Key`가 지원되는 지에 대해서는 고민하실 필요가 없습니다.
    - 문서와 관련된 정보라면 어떤 정보든 저장하시면 됩니다. 문서 내용에서 핵심 키워드를 뽑아서 `keywords` 키로 저장하거나, 요약을 `summary` 키로 저장하기도 합니다.
    - PDF Loader 경우에도 PDF Loader 종류에 따라 설정해주는 메타 데이터가 다릅니다.

::::{tab-set}

:::{tab-item} 파이썬 코드로 간결하게 문서 변환

```{code-block} python
:linenos:

from typing import List
from pprint import pprint
from langchain_core.documents import Document

def load() -> List[Document]:
    file_path = "빽다방.txt"
    지식: str = open(file_path, "rt", encoding="utf-8").read()
    docs = [
        Document(
            # 의미있는 메타데이터가 있다면, 맘껏 더 담으시면 됩니다.
            metadata={"source": file_path},
            page_content=지식,
        )
    ]
    return docs

doc_list = load()
print(f"loaded {len(doc_list)} documents")
pprint(doc_list)
```
:::

:::{tab-item} 랭체인을 활용해서 문서 변환

```{code-block} python
:linenos:
:emphasize-lines: 5-7,10-12

from typing import List
from pprint import pprint
from langchain_core.documents import Document

# 예전에는 `langchain` 라이브러리 기본에서 다양한 `Loader`를 지원했지만,
# 요즘은 `langchain-community` 라이브러리 등 외부 라이브러리로 지원하는 경우가 많습니다.
from langchain_community.document_loaders import TextLoader

def load() -> List[Document]:
    file_path = "빽다방.txt"
    loader = TextLoader(file_path=file_path)
    docs: List[Document] = loader.load()
    return docs

doc_list = load()
print(f"loaded {len(doc_list)} documents")
pprint(doc_list)
```
:::

::::

두 코드 모두 동일한 출력을 반환합니다.

```{code-block} text
loaded 1 documents
[Document(metadata={'source': '빽다방.txt'}, page_content='1. 아이스티샷추가(아.샷.추)\n  - SNS에서 더 유명한 꿀팁 조합 음료 :) 상콤달콤한 복숭아맛 아이스티에 진한 에스프레소 샷이 어우러져 환상조합\n  - 가격: 3800원\n\n2. 바닐라라떼(ICED)\n  - 부드러운 우유와 달콤하고 은은한 바닐라가 조화를 이루는 음료\n  - 가격: 4200원\n\n3. 사라다빵\n  - 빽다방의 대표메뉴 :) 추억의 감자 사라다빵\n  - 가격: 3900원\n\n4. 빽사이즈 아메리카노(ICED)\n  - 에스프레소 4샷이 들어가 깊고 진한 맛의 아메리카노\n  - 가격: 3500원\n\n5. 빽사이즈 원조커피(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) [주의. 564mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원\n\n6. 빽사이즈 원조커피 제로슈거(ICED)\n  - 빽다방의 BEST메뉴를 더 크게, 제로슈거로 즐겨보세요 :) [주의. 686mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원\n\n7. 빽사이즈 달콤아이스티(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) 시원한 복숭아맛 아이스티\n  - 가격: 4300원\n\n8. 빽사이즈 아이스티샷추가(ICED)\n  - SNS에서 더 유명한 꿀팁 조합 음료 :) 상콤달콤한 복숭아맛 아이스티에 진한 에스프레소 2샷이 어우러져 환상조합\n  - 가격: 4800원\n\n9. 빽사이즈 아이스티 망고추가+노란빨대\n  - SNS핫메뉴 아이스티에 망고를 한가득:)\n  - 가격: 6300원\n\n10. 빽사이즈 초코라떼(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) 진짜~완~전 진한 초코라떼\n  - 가격 : 5500원\n')]
```

RAG 에서는 질문과 유사한 문서를 문서 단위로 찾아서, 프롬프트에 적용합니다.
각각의 문서는 아래 조건을 만족하면, 보다 좋은 RAG 결과를 얻을 수 있습니다.

1. 한 문서에 여러 주제가 섞여 있지 않고, 단일 핵심 정보를 적절한 크기로 포함할 것
    - 불필요한 정보까지 함께 제공하게 됩니다.
    - 문서의 내용이 너무 짧거나 부족하면, 여러 문서를 검색해야 하므로 RAG 성능이 저하됩니다.
2. 일정한 구조를 유지할 것
3. 관련없는 정보를 제거할 것
4. 다른 문서와 중복되지 않도록 구성할 것
5. 적절한 메타 데이터를 포함할 것

```{admonition} 보다 좋은 RAG 결과를 얻기 위해서는.
:class: warning

원본 지식 데이터를 처리할 때, 단순히 파일 내용을 텍스트로 변환하는 것만으로는 충분하지 않을 수 있습니다.
랭체인(LangChain)을 사용하든 직접 구현하든, 변환된 텍스트 문서가 효과적으로 검색되고 활용될 수 있도록 구조화하고 최적화하여,
**원본 지식 데이터의 품질을 관리하는 것**이 핵심입니다.

하지만, 원본 지식 데이터가 방대할 경우 각 문서의 내용을 일일이 조정하고 검수하는 것은 어려울 수 있습니다.
```

## 2단계. Split - 각 문서들을 쪼개기

`Load` 단계에서 생성된 문서를 쪼개어 여러 문서로 나누는 `Split` 단계입니다.
문서의 내용을 변경하는 것은 아니구요. 문서의 포맷은 유지한 채 문서를 쪼개어 여러 문서로 나누는 과정입니다.

+ 하나의 문서가 너무 길면, LLM 모델에 전달할 수 없습니다.
+ 하나의 문서가 너무 길면, LLM에서 너무 많은 정보를 포착하려고 합니다.
+ 하나의 문서에 여러 주제가 섞여 있는 경우, 각 주제를 쪼개어 여러 문서로 나누는 것이 RAG 성능을 향상시키는 데 도움이 됩니다.

```{figure} ./assets/typical-splits.png
:alt: (RAG) Indexing

출처 : [랭체인 공식 튜토리얼: Text Splitters](https://python.langchain.com/docs/concepts/text_splitters/)
```

아래와 같이 한 문서에 여러 메뉴 정보가 섞여 있다면 각 메뉴 정보를 쪼개어 여러 문서로 나누는 것이 RAG 성능을 향상시키는 데 도움이 됩니다.

::::{tab-set}

:::{tab-item} 쪼개기 전 문서들

첫번째 문서의 `.page_content`

```{code-block} text

1. 아이스티샷추가(아.샷.추)
  - SNS에서 더 유명한 꿀팁 조합 음료 :) 상콤달콤한 복숭아맛 아이스티에 진한 에스프레소 샷이 어우러져 환상조합
  - 가격: 3800원

2. 바닐라라떼(ICED)
  - 부드러운 우유와 달콤하고 은은한 바닐라가 조화를 이루는 음료
  - 가격: 4200원

3. 사라다빵
  - 빽다방의 대표메뉴 :) 추억의 감자 사라다빵
  - 가격: 3900원
```

두번째 문서의 `.page_content`

```{code-block} text

4. 빽사이즈 아메리카노(ICED)
  - 에스프레소 4샷이 들어가 깊고 진한 맛의 아메리카노
  - 가격: 3500원

5. 빽사이즈 원조커피(ICED)
  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) [주의. 564mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]
  - 가격: 4000원
```
:::

:::{tab-item} 나눠진 각 문서의 `.page_content`

나눠진 문서의 `.page_content`

```{code-block} text

1. 아이스티샷추가(아.샷.추)
  - SNS에서 더 유명한 꿀팁 조합 음료 :) 상콤달콤한 복숭아맛 아이스티에 진한 에스프레소 샷이 어우러져 환상조합
  - 가격: 3800원
```

나눠진 문서의 `.page_content`

```{code-block} text

2. 바닐라라떼(ICED)
  - 부드러운 우유와 달콤하고 은은한 바닐라가 조화를 이루는 음료
  - 가격: 4200원
```

나눠진 문서의 `.page_content`

```{code-block} text

3. 사라다빵
  - 빽다방의 대표메뉴 :) 추억의 감자 사라다빵
  - 가격: 3900원
```

나눠진 문서의 `.page_content`

```{code-block} text

4. 빽사이즈 아메리카노(ICED)
  - 에스프레소 4샷이 들어가 깊고 진한 맛의 아메리카노
  - 가격: 3500원
```

나눠진 문서의 `.page_content`

```{code-block} text

5. 빽사이즈 원조커피(ICED)
  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) [주의. 564mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]
  - 가격: 4000원
```
:::

::::

문서의 양이 작다면 사람이 일일이 쪼갤 수도 있겠지만, 대개 문서의 양이 많기 때문에 일괄적인 룰을 적용해서 쪼개는 경우가 많습니다.
[랭체인 공식 튜토리얼](https://python.langchain.com/docs/concepts/text_splitters/#approaches)에서는 다음 4가지 전략을 언급하고 있습니다.

1. **길이**에 기반한 쪼개기
    - 직관적이고 구현이 간단하지만, 텍스트 구조나 의미를 고려하지 않으므로 문맥 단절 가능성이 큽니다.
    - 위 데이터처럼 각 메뉴마다 구분자가 `"\n\n"`처럼 일관되게 잘 지정되어있으면, 좋은 결과를 얻을 수 있습니다.
    - 랭체인 : [`CharacterTextSplitter`](https://python.langchain.com/api_reference/text_splitters/character/langchain_text_splitters.character.CharacterTextSplitter.html), [`RecursiveCharacterTextSplitter`](https://python.langchain.com/api_reference/text_splitters/character/langchain_text_splitters.character.RecursiveCharacterTextSplitter.html) (많이 사용 ⭐️)
2. **텍스트 구조**에 기반한 쪼개기
    - 문단, 헤더, 목록 등의 텍스트 구조를 고려해서 쪼갭니다.
    - 하지만 문서마다 텍스트 구조가 다를 수 밖에 없으므로 적용이 제한적입니다.
    - 랭체인 : [`NltkTextSplitter`](https://python.langchain.com/api_reference/text_splitters/nltk/langchain_text_splitters.nltk.NLTKTextSplitter.html#langchain_text_splitters.nltk.NLTKTextSplitter), [`SpacyTextSplitter`](https://python.langchain.com/api_reference/text_splitters/spacy/langchain_text_splitters.spacy.SpacyTextSplitter.html#langchain_text_splitters.spacy.SpacyTextSplitter) 등
3. **문서 구조**에 기반한 쪼개기
    - 특정 문서 포맷 (HTML, Markdown 등)의 계층적 구조 (섹션, 하위 섹션 등)를 고려해서 쪼갭니다.
    - 구조가 복잡한 문서일수록 분할 로직이 복잡해지고, 일부 영역은 누락될 수 있습니다.
    - 랭체인
        - [`HTMLHeaderTextSplitter`](https://python.langchain.com/api_reference/text_splitters/html/langchain_text_splitters.html.HTMLHeaderTextSplitter.html#langchain_text_splitters.html.HTMLHeaderTextSplitter), [`HTMLSectionSplitter`](https://python.langchain.com/api_reference/text_splitters/html/langchain_text_splitters.html.HTMLSectionSplitter.html)
        - [`MarkdownTextSplitter`](https://python.langchain.com/api_reference/text_splitters/markdown/langchain_text_splitters.markdown.MarkdownTextSplitter.html), [`MarkdownHeaderTextSplitter`](https://python.langchain.com/api_reference/text_splitters/markdown/langchain_text_splitters.markdown.MarkdownHeaderTextSplitter.html), [`ExperimentalMarkdownSyntaxTextSplitter`](https://python.langchain.com/api_reference/text_splitters/markdown/langchain_text_splitters.markdown.ExperimentalMarkdownSyntaxTextSplitter.html) 등
4. **의미** (Semantic meaning)에 기반한 쪼개기
    - 의미적으로 연관된 단락을 하나로 묶어 문맥을 가장 잘 유지하며, 중요 문단만 효율적으로 추려낼 수 있습니다.
    - 의미 분석을 위한 별도의 프로세스가 필요합니다.
    - 분석 결과가 부정확할 경우, 의도와 다르게 분할되거나 누락될 수도 있습니다.
    - 랭체인
        - [`HTMLSemanticPreservingSplitter`](https://python.langchain.com/api_reference/text_splitters/html/langchain_text_splitters.html.HTMLSemanticPreservingSplitter.html) 등

[빽다방.txt](./빽다방.txt) 데이터는 각 메뉴가 구분자로 `"\n\n"`로 구분되어 있습니다. 그러니 아래와 같이 문자열의 `.split("\n\n")` 메서드를 사용해서 문서 내용을 쪼갤 수 있습니다. 쪼개어진 문서는 원본 문서의 메타 데이터를 그대로 가져갑니다.

```{code-block} python
:linenos:
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

실행해보시면, 아래와 같이 각 메뉴들이 각각의 문서로 쪼개진 것을 확인할 수 있습니다.

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

```{admonition} 원본 데이터 변환이 가장 어렵고 중요합니다.
:class: important

`Load` 단계에서 원본 지식을 명확히 이해하고 그에 맞게 변환을 해야만, 이후 `Split` 과정을 손쉽게 진행할 수 있으며 정보 누락이나 문맥 단절도 최소화할 수 있습니다.
```

## 3단계. Embed - 각 문서들을 벡터 데이터로 미리 변환하여, 유사도 검색 준비

### 유사 문서를 찾을려면?

컴퓨터는 문자열 그 자체로 의미를 파악할 수는 없구요. 컴퓨터는 계산기이기 때문에 문자열을 숫자로 변환을 해야 합니다. 이러한 숫자를 벡터(Vector)라고 부르며, 벡터로의 변환 과정을 임베딩(Embedding)이라고 합니다.
벡터 변환은 OpenAI의 `text-embedding-3-small` 임베딩 모델로 변환을 했구요. 이 모델은 1536 차원의 고정 크기의 벡터를 반환합니다.

+ `"오렌지"` → `[0.012021134607493877, -0.050807174295186996, ...]` (1536 개의 실수 배열)
+ `"설탕 커피"` → `[-0.0008126725442707539, -0.03418251499533653, ...]` (1536 개의 실수 배열)
+ `"카푸치노"` → `[-0.02137843146920204, 0.0011899990495294333, ...]` (1536 개의 실수 배열)
+ `"coffee"` → `[-0.01013763528317213, 0.0037400354631245136, ...]` (1536 개의 실수 배열)

각 벡터 값을 가지고, 유사 문서를 찾아내는 방법은 **코사인 유사도**, 유클리드 거리, 맨해튼 거리, 점수 기반 유사도, 자카드 유사도, **BM25** 등이 있습니다.

이 중에 가장 많이 대중적인 방법은 **코사인 유사도**이며 두 벡터 간의 각도의 코사인 값을 이용하여 벡터 간의 유사도를 측정합니다.
코사인 유사도 값의 범위는 코사인 값 범위인 `-1 ≤ cos(θ) ≤ 1` 입니다. 같은 방향이면 각도가 0이니 `cos(0) = 1` 로 계산됩니다.

+ `1.0` → 완전히 동일한 벡터 (매우 유사함)
+ `0.5` → 어느 정도 관련 있음
+ `0.0` → 완전히 독립적인 의미 (연관 없음)
+ `-1.0` → 완전히 반대되는 방향 (극단적으로 다름)

```{figure} ./assets/typical-cosine-similarity.png
:alt: Cosine Similarity

출처 : [What is Cosine Similarity? How to Compare Text and Images in Python](https://towardsdatascience.com/what-is-cosine-similarity-how-to-compare-text-and-images-in-python-d2bb6e411ef0)
```

`"커피"` 문자열과 유사한 단어를 찾아볼려고 합니다. `"커피"` 문자열의 벡터 값은 `[-0.03496772050857544, -0.007349129766225815, ...]` 이구요. "오렌지", "설탕 커피", "카푸치노", "coffee" 문자열 과의 코사인 유사도를 계산해보면 다음과 같습니다. (`scikit-learn` 라이브러리에서 [`cosine_similarity`](https://scikit-learn.org/dev/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html) 함수를 지원해줍니다.)

+ 의존 라이브러리 : `pip install -U scikit-learn`

```{code-block} python
:linenos:

>>> from sklearn.metrics.pairwise import cosine_similarity
>>> cosine_similarity([커피_벡터], [오렌지_벡터, 설탕_커피_벡터, 카푸치노_벡터, coffee_벡터])
array([[0.24943755, 0.49060672, 0.24737702, 0.44323739]])
```

"커피" 문자열과

1. 가장 유사한 문자열은 "설탕 커피" (유사도: 0.49060672)
2. 두번째로 유사한 문자열은 "coffee" (유사도: 0.44323739)
3. 세번째로 유사한 문자열은 "오렌지" (유사도: 0.24943755)
4. 네번째로 유사한 문자열은 "카푸치노" (유사도: 0.24737702)

"카푸치노" 보다 "오렌지"가 더 유사하다고 측정되었습니다.
"카푸치노" 는 커피 종류이지만 문자 구조 자체는 "커피"와 비교적 거리가 멀 수 있습니다.
어떤 임베딩 모델을 사용했는 지와 측정 방법에 따라 유사도 측정 결과가 달라질 수 있으니, 단순히 유사도 값만 봐서는 안 되겠습니다. 😅

### 문서 임베딩 구현

앞서 생성했던 빽다방 메뉴 데이터를 벡터 데이터로 변환하겠습니다. `embed` 함수에서는 문서 리스트를 받고, 각 문서의 내용(`.page_content`)을 임베딩 모델을 통해 벡터 데이터로 변환합니다. 각 원본 문자열과 벡터 데이터는 리스트에 담아서 반환합니다. 이렇게 생성된 벡터 데이터를 저장하고 관리하는 주체를 `Vector Store` 라고 부릅니다.

```{code-block} python
:linenos:

def embed(doc_list: List[Document]) -> List[Dict]:
    vector_store = []

    for doc in doc_list:
        text = doc.page_content
        response = client.embeddings.create(
            model="text-embedding-3-small",  # 1536 차원
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
            row["text"][:10], len(row["embedding"]), row["embedding"][:2]
        )
    )
```

아래와 같이 각 메뉴들이 개별 문서로 `Split`되었고, 각 문서가 1536차원의 벡터 배열로 변환되었음을 확인하실 수 있습니다.

```{code-block} text
loaded 1 documents
split into 10 documents
created 10 items in vector store
1. 아이스티샷추가... => 1536 차원, [-0.02693873643875122, -0.043540798127651215] ...
2. 바닐라라떼(I... => 1536 차원, [0.02490091510117054, -0.04808296635746956] ...
3. 사라다빵  ... => 1536 차원, [0.027449999004602432, -0.04239306598901749] ...
4. 빽사이즈 아메... => 1536 차원, [-0.009449880570173264, -0.03460339829325676] ...
5. 빽사이즈 원조... => 1536 차원, [0.03321684151887894, 0.035661567002534866] ...
6. 빽사이즈 원조... => 1536 차원, [0.04160701856017113, -0.0009915598202496767] ...
7. 빽사이즈 달콤... => 1536 차원, [0.014812068082392216, -0.01777448132634163] ...
8. 빽사이즈 아이... => 1536 차원, [-0.011549889110028744, -0.02412295714020729] ...
9. 빽사이즈 아이... => 1536 차원, [0.009231451898813248, 0.050084274262189865] ...
10. 빽사이즈 초... => 1536 차원, [0.0744316577911377, 0.013424741104245186] ...
```

## 4단계. Store - 변환된 벡터 데이터를 디스크에 저장

`list` 클래스를 확장한 `VectorStore` 클래스를 구현하여, `VectorStore` 내에서 벡터 데이터를 저장하고 관리할 수 있도록 구현해보겠습니다.
다음 4가지 기능을 지원합니다.

1. `make` 메서드 : 문서 리스트를 받아서 벡터 데이터 리스트를 생성 (`Embed` 단계)
2. `save` 메서드 : 현재의 벡터 데이터 리스트를 디스크에 파일로 저장
3. `load` 메서드 : 디스크에 저장된 벡터 데이터를 로딩하여 리스트 화
4. `search` 메서드 : 질문 문자열을 받아서 유사 문서 목록을 검색

### `embed` 함수를 `make` 메서드로 리팩토링

먼저 위에서 구현한 `embed` 함수를 `VectorStore.make` 클래스 함수로 리팩토링합니다.

```{code-block} python
:linenos:

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

### `save` 메서드와 `load` 메서드 구현

벡터 데이터가 메모리에만 저장되어있는 상황이기에 프로세스가 종료되면 데이터가 사라집니다. 따라서 데이터를 디스크에 저장하고 관리할 필요가 있습니다.

데이터는 변경되지 않았는 데, 문서 검색이 필요할 때마다 매번 모든 문서에 대해서 임베딩을 수행하고 VectorStore를 생성하는 것은 비효율적입니다.
디스크에 파일로서 저장해야만 프로세스가 종료되어도 데이터가 유지되며, 필요할 때 파일을 읽어 사용할 수 있습니다.
파이썬 객체를 파일로 저장하는 가장 간단한 방법으로서 [`pickle`이 파이썬 기본에서 지원](https://docs.python.org/ko/3.13/library/pickle.html)됩니다.
물론 JSON이나 CSV 등 다양한 포맷으로 저장할 수 있습니다.

```{code-block} python
:linenos:

import pickle
from pathlib import Path

class VectorStore(list):
    # ...

    def save(self, vector_store_path: Path) -> None:
        """
        현재의 벡터 데이터 리스트를 지정 경로에 파일로 저장
        """
        with vector_store_path.open("wb") as f:
            # 리스트(self)를 pickle 포맷으로 파일(f)에 저장
            pickle.dump(self, f)

    @classmethod
    def load(cls, vector_store_path: Path) -> "VectorStore":
        """
        지정 경로에 저장된 파일을 읽어서 벡터 데이터 리스트를 반환
        """
        with vector_store_path.open("rb") as f:
            # pickle 포맷으로 파일(f)에서 리스트(VectorStore)를 로딩
            return pickle.load(f)
```

### `search` 메서드 구현

다음 [](./typical-03) 단계에서 구현하겠습니다.

## `VectorStore` 클래스 현재 상황

```{code-block} python
:linenos:

import pickle
from pathlib import Path
from typing import List

import numpy as np
import openai
from langchain_community.utils.math import cosine_similarity
from langchain_core.documents import Document


client = openai.Client()


def load() -> List[Document]:
    file_path = "빽다방.txt"
    지식: str = open(file_path, "rt", encoding="utf-8").read()
    docs = [
        Document(
            # 의미있는 메타데이터가 있다면, 맘껏 더 담으시면 됩니다.
            metadata={"source": file_path},
            page_content=지식,
        )
    ]
    return docs


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

    def save(self, vector_store_path: Path) -> None:
        """
        현재의 벡터 데이터 리스트를 지정 경로에 파일로 저장
        """
        with vector_store_path.open("wb") as f:
            # 리스트(self)를 pickle 포맷으로 파일(f)에 저장
            pickle.dump(self, f)

    @classmethod
    def load(cls, vector_store_path: Path) -> "VectorStore":
        """
        지정 경로에 저장된 파일을 읽어서 벡터 데이터 리스트를 반환
        """
        with vector_store_path.open("rb") as f:
            # pickle 포맷으로 파일(f)에서 리스트(VectorStore)를 로딩
            return pickle.load(f)
```

위에서 생성된 `VectorStore` 클래스를 다음과 같이 활용할 수 있습니다.

1. 첫번째 실행에서는 vector_store.pickle 파일이 없으므로 load, split, make, save 순서로 데이터를 생성하고 저장합니다.
2. 이후 실행에서는 vector_store.pickle 파일이 있으므로 load 순서로 데이터를 로딩합니다.
3. TODO: [](./typical-03) 단계에서 질문을 받고, RAG를 통해 답변을 구현하겠습니다.

```{code-block} python
:linenos:

def main():
    vector_store_path = Path("vector_store.pickle")

    if not vector_store_path.is_file():
        doc_list = load()
        print(f"loaded {len(doc_list)} documents")
        doc_list = split(doc_list)
        print(f"split into {len(doc_list)} documents")
        vector_store = VectorStore.make(doc_list)
        vector_store.save(vector_store_path)
        print(f"created {len(vector_store)} items in vector store")
    else:
        vector_store = VectorStore.load(vector_store_path)
        print(f"loaded {len(vector_store)} items in vector store")

    # TODO: 질문을 받고, RAG를 통해 답변을 구현하겠습니다.
    question = input("질문을 입력하세요: ")

if __name__ == "__main__":
    main()
```
