# #01. 랭체인 코드와 파이썬 코드 비교

매 질문마다 질문 맥락에 맞는 지식을 찾아서 제공하는 전형적인 RAG를 바닥부터 구현해보겠습니다.

랭체인 등의 라이브러리를 사용하면 RAG를 손쉽게 구현할 수 있지만, 보통 기계적으로 코드를 복붙해서 사용할 뿐 이고,
약간의 변경에 대해서도 대응하기 어렵습니다. RAG 뿐만 아니라 랭체인의 많은 기능들을 먼저 이해해야 하기 때문이죠.

**RAG도 결국 프롬프트 문자열을 구성하는 과정**이기 때문에, 파이썬 코드 만으로도 충분히 구현할 수 있습니다.
RAG 과정을 바닥부터 구현하여 데이터 변환, 임베딩, 검색 등의 과정들이 어떻게 연결되는 지 직접 경험해봅시다.
이는 추후 최적화나 커스텀 기능을 구현할 때 도움이 될 것입니다.

## 랭체인 활용 vs 파이썬 직접 구현

[랭체인 RAG 공식 튜토리얼](https://python.langchain.com/docs/tutorials/rag/)을 살펴보시면,
파이썬에 익숙하시더라도 코드를 읽기가 쉽지 않습니다.

랭체인을 사용하시더라도 랭체인의 모든 기능을 반드시 활용하셔야 하는 것은 아닙니다. 필요한 기능을 선택적으로 활용할 수 있는 능력을 키워야하겠구요.
기능에 따라, 파이썬 코드로 직접 구현하는 것이 더 유연하고 확장성이 높을 수 있습니다.

RAG에서는 웹페이지 내용을 로딩하여 지식으로 활용하기도 하는 데요.
이 과정을 랭체인을 활용한 예시와 파이썬으로 직접 구현한 예시를 비교해보겠습니다.
아래 두 개 코드는 거의 동일한 `docs` 객체. 문서 리스트를 생성합니다.

```{code-block} bash
# "랭체인을 통해 웹페이지 내용을 문서로 변환" 코드 실행을 위한 라이브러리 설치
pip install -U requests beautifulsoup4 langchain langchain-community 

# "파이썬 코드로 직접 웹페이지 내용을 문서로 변환" 코드 실행을 위한 라이브러리 설치
pip install -U requests beautifulsoup4
pip install -U langchain  # Document 타입 지정을 위해서만 필요
```

::::{tab-set}

:::{tab-item} 랭체인을 통해 웹페이지 내용을 문서로 변환

랭체인의 `WebBaseLoader`를 사용하고 옵션을 지정하면 알아서 웹페이지 내용을 문서로 변환해줍니다.

+ HTML 파싱 룰을 제한적으로만 지원해줍니다.
+ 내부에서 `requests` 라이브러리를 통해 요청을 하므로, HTML 응답을 하는 정적 웹페이지에 한해서만 사용 가능합니다.
    - JS로 동작하는 웹페이지를 지원하는 [`AsyncChromiumLoader`](https://python.langchain.com/v0.1/docs/use_cases/web_scraping/#asyncchromiumloader)가 있지만, 유지보수가 잘 되지 않고 사용할 수 있는 옵션이 제한적입니다.

```{code-block} python
:linenos:

import bs4
from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader

bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs={"parse_only": bs4_strainer},
)
docs: list[Document] = loader.load()
print(f"loaded {len(docs)} documents")
for doc in docs:
    print(doc.metadata)
```

:::

:::{tab-item} 파이썬 코드로 직접 웹페이지 내용을 문서로 변환

일반적인 HTTP 요청 코드를 작성하여 웹페이지 내용을 가져오고 직접 문서로 변환합니다.

+ HTML 파싱 룰을 자유자재로 지정할 수 있습니다.
+ 직접 HTTP Client를 사용하므로, 다양한 Headless Browser(Selenium, Playwright, Puppeteer, Splash 등)를 사용할 수 있고 커스텀 옵션을 지정할 수 있습니다.
+ 파이썬으로 HTTP 요청을 하는 예시와 라이브러리가 다양하므로, **검색이나 ChatGPT를 통해 도움을 받기 쉽습니다.**

```{code-block} python
:linenos:

import requests
import bs4
from langchain_core.documents import Document

res = requests.get("https://lilianweng.github.io/posts/2023-06-23-agent/")
soup = bs4.BeautifulSoup(res.text)
tags = soup.select(".post-title, .post-header, .post-content")
text = "\n\n".join(tag.text for tag in tags)

doc = Document(
    metadata={"source": "https://lilianweng.github.io/posts/2023-06-23-agent/"},
    page_content=text,
)
docs: list[Document] = [doc]
print(f"loaded {len(docs)} documents")
for doc in docs:
    print(doc.metadata)
```

:::

::::

```{admonition} Document는 단순히 문서 내용과 메타데이터를 담는 데이터 구조
:class: tip

+ `.metadata` : 메타 데이터 (타입: `Dict`)
+ `.page_content` : 문서 내용 (타입: `str`)

`doc = Document(metadata={"source": "URL"}, page_content=내용)`
```

두 코드 모두 동일하게 문서를 생성해냅니다.

```{code-block} text
loaded 1 documents
{'source': 'https://lilianweng.github.io/posts/2023-06-23-agent/'}
```

랭체인을 쓰시더라도 랭체인의 모든 기능을 쓰실려고 하실 필요는 없구요.
랭체인의 특정 기능 업데이트를 기다리실 필요도 없습니다.
**이처럼 필요한 기능은 파이썬 코드로 직접 구현하실 수 있습니다.**

## 본 튜토리얼의 랭체인 버전

[](./langchain)를 살펴보시면, 각각의 코드가 어떤 기능을 하는 지 한 눈에 파악이 되시나요?
파이썬 코드이지만 랭체인 코드 스타일이 낯설지 않으신가요?
아직 RAG 과정에 대한 이해가 없으니 랭체인 코드도 잘 읽히지 않으실텐데요.

랭체인없이 파이썬 코드 만으로 RAG 과정을 구현해보며 RAG에 대한 이해를 높여보겠습니다.
본 튜토리얼이 끝나면 아래 랭체인 코드도 보다 쉽게 읽히실 것입니다.

```{code-block} python
:linenos:
:caption: 일부 코드

llm = ChatOpenAI(model_name="gpt-4o-mini")
retriever = vector_store.as_retriever()
prompt_template = PromptTemplate(
    template="Context: {context}\n\nQuestion: {question}\n\nAnswer:",
    input_variables=["context", "question"],
)

rag_pipeline = (
    RunnableLambda(
        lambda x: {
            "context": retriever.invoke(x),
            "question": x,
        }
    )
    | prompt_template
    | llm
)
ai_message: AIMessage = rag_pipeline.invoke(question)
print("[AI]", ai_message.content)  # AIMessage 타입
print(ai_message.usage_metadata)
```
