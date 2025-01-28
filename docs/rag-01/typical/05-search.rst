5단계. 지식 검색 (Search) 및 LLM 요청/응답
===========================================

  저장된 지식을 검색하여 LLM에게 전달하고 최종 응답을 생성하는 과정

본 페이지는 59:33 지점부터 1:13:10 지점까지 보시면 됩니다.

.. raw:: html

  <div class="video-container">
    <iframe
        src="https://www.youtube.com/embed/9ayknWI-VcI?start=3573"
        frameborder="0"
        allowfullscreen>
    </iframe>
  </div>

----

필요성
----------

RAG 시스템의 목적은 LLM이 검색된 정보를 중심으로 답변하도록 유도하는 것입니다.

.. figure:: ./assets/typical-retrieval-and-generation.png
   :alt: (RAG) Retrieval and Generation

   출처 : `랭체인 공식 튜토리얼: RAG 애플리케이션 구축하기 <https://python.langchain.com/docs/tutorials/rag/>`_

#. Question : 유저로부터 질문 받기
#. Retrieve : 질문에 대한 정보가 저장된 Vector Store에서 질문과 유사도가 높은 문서들을 k개 찾기 
#. Prompt : 질문과 찾은 문서들을 프롬프트에 포함시켜 LLM에게 요청

각 단계를 순차적으로 수행하고 유저에게 답변을 전달합니다.
잘못된 문서가 검색되더라도 이를 검증하는 단계는 없습니다.

.. tip::
   질문과 유사 문서의 품질을 평가해서, 재질문 혹은 문서 재검색을 수행할 수도 있습니다.

   RAG 검색 과정이 무조건 Question → Retrieve → Prompt 순서로 진행해야만 하는 것은 아닙니다.
   다양한 프로세스가 있을 수 있습니다. **코드로 구현하기 나름**\입니다.

   질문과 유사 문서의 품질을 평가해서, 재질문 혹은 문서 재검색을 수행할 수도 있습니다.
   이러한 Flow를 파이썬 코드로 직접 구현할 수도 있겠구요.
   ``LangGraph`` 라이브러리를 통해 Flow 구성을 좀 더 직관적으로 하실 수도 있습니다.
   ``LangGraph``\가 필수인 것은 아닙니다. 하나의 선택지일 뿐입니다.


파이썬 구현
----------------

``VectorStore`` 클래스에 ``search`` 메서드 구현
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

먼저 질문과 유사한 문서를 찾아주는 ``search`` 메서드를 ``VectoreStore`` 클래스에 구현해봅시다.

1. 인자로 질문과 찾고자 하는 유사 문서 개수를 받습니다.

   - 유사 문서 개수는 디폴트로 ``4``\를 지정했구요. 랭체인에서도 디폴트로 ``4``\입니다.

2. 질문 문자열을 임베딩 벡터 배열로 변환합니다.

3. 질문과 VectorStore 내에 저장된 모든 문서들과 코사인 유사도를 계산합니다.

4. 유사도가 높은 순으로 정렬하여 ``k``\개를 반환합니다.

.. code-block:: python
   :linenos:
   :emphasize-lines: 2-3,12-36

   import openai
   import numpy as np
   from sklearn.metrics.pairwise import cosine_similarity

   client = openai.Client()

   class VectorStore(list):
       embedding_model = "text-embedding-3-small"

       # ...

       def search(self, question: str, k: int = 4) -> List[Document]:
           """
           질의 문자열을 받아서, 벡터 스토어에서 유사 문서를 최대 k개 반환
           """

           # 질문 문자열을 임베딩 벡터 배열로 변환
           response = client.embeddings.create(
               model=self.embedding_model,
               input=question,
           )
           question_embedding = response.data[0].embedding  # 1536 차원, float 배열

           # VectorStore 내에 저장된 모든 벡터 데이터를 리스트로 추출
           embedding_list = [row["embedding"] for row in self]

           # 모든 문서와 코사인 유사도 계산
           similarities = cosine_similarity([question_embedding], embedding_list)[0]
           # 유사도가 높은 순으로 정렬하여 k 개 선택
           top_indices = np.argsort(similarities)[::-1][:k]

           # 상위 k 개 문서를 리스트로 반환
           return [
               self[idx]["document"].model_copy()
               for idx in top_indices
           ]

1단계. Question
~~~~~~~~~~~~~~~~~~~~

RAG를 수행할 질문을 먼저 정의합니다.

.. code-block:: python
   :linenos:

   question = "빽다방 카페인이 높은 음료와 가격은?"


2단계. Retrieve
~~~~~~~~~~~~~~~~~~~~

``vector_store`` 에서 질문과 유사한 문서를 찾아서, 프롬프트에 바로 사용할 수 있도록 ``지식`` 문자열 변수로 저장합니다.

.. code-block:: python
   :linenos:

   search_doc_list: List[Document] = vector_store.search(question)
   pprint(search_doc_list)

   print("## 지식 ##")
   지식: str = str(search_doc_list)
   print(repr(지식))

아래와 같이 유사 문서를 찾아, ``지식`` 문자열까지 잘 생성했습니다.

.. code-block:: text

   [Document(metadata={'source': '빽다방.txt'}, page_content='5. 빽사이즈 원조커피(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) [주의. 564mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원'),
    Document(metadata={'source': '빽다방.txt'}, page_content='6. 빽사이즈 원조커피 제로슈거(ICED)\n  - 빽다방의 BEST메뉴를 더 크게, 제로슈거로 즐겨보세요 :) [주의. 686mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원'),
    Document(metadata={'source': '빽다방.txt'}, page_content='3. 사라다빵\n  - 빽다방의 대표메뉴 :) 추억의 감자 사라다빵\n  - 가격: 3900원'),
    Document(metadata={'source': '빽다방.txt'}, page_content='2. 바닐라라떼(ICED)\n  - 부드러운 우유와 달콤하고 은은한 바닐라가 조화를 이루는 음료\n  - 가격: 4200원')]
   ## 지식 ##
   "[Document(metadata={'source': '빽다방.txt'}, page_content='5. 빽사이즈 원조커피(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) [주의. 564mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원'), Document(metadata={'source': '빽다방.txt'}, page_content='6. 빽사이즈 원조커피 제로슈거(ICED)\n  - 빽다방의 BEST메뉴를 더 크게, 제로슈거로 즐겨보세요 :) [주의. 686mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원'), Document(metadata={'source': '빽다방.txt'}, page_content='3. 사라다빵\n  - 빽다방의 대표메뉴 :) 추억의 감자 사라다빵\n  - 가격: 3900원'), Document(metadata={'source': '빽다방.txt'}, page_content='2. 바닐라라떼(ICED)\n  - 부드러운 우유와 달콤하고 은은한 바닐라가 조화를 이루는 음료\n  - 가격: 4200원')]"

3단계. Prompt
~~~~~~~~~~~~~~~~~~~~

:doc:`../glance` 에서는 모든 지식을 한 번에 프롬프트에 주입했었었구요.

이번에는 "빽다방 카페인이 높은 음료와 가격은?" 질문과 유사한 문서로만 잘 검색이 되었고 이를 프롬프트에 주입하겠습니다.

.. code-block:: python
   :linenos:

   res = client.chat.completions.create(
       messages=[
           {
               "role": "system",
               "content": f"넌 AI Assistant. 모르는 건 모른다고 대답.\n\n[[빽다방 메뉴 정보]]\n{지식}",
           },
           {
               "role": "user",
               "content": question,
           },
       ],
       model="gpt-4o-mini",
       temperature=0,
   )
   print()
   print("[AI]", res.choices[0].message.content)
   print_prices(res.usage.prompt_tokens, res.usage.completion_tokens)

RAG 답변을 받아보면, 검색된 지식에 기반해서 정확한 답변을 받았음을 확인하실 수 있습니다. 😉

.. code-block:: text

   [AI] 빽다방에서 카페인이 높은 음료는 다음과 같습니다:

   1. 빽사이즈 원조커피(ICED) - 564mg 고카페인, 가격: 4000원
   2. 빽사이즈 원조커피 제로슈거(ICED) - 686mg 고카페인, 가격: 4000원

   이 두 음료가 카페인이 가장 높습니다.
   input: tokens 293, krw 0.0659
   output: tokens 93, krw 0.083700

전체 코드
---------------

``VectorStore.make`` 메서드 내에서 ``metadata``\를 추가로 저장하고, ``search`` 메서드에서도 기존 문서의 ``metadata``\를 추출해서 사용토록 개선했습니다.

.. warning::

   데이터 포맷이 변경되었으므로 기존 ``vector_store.pickle`` 파일을 삭제하시고 pickle 파일을 다시 생성해주세요.
   재생성하지 않고 기존 pickle 데이터로 실행하시면 ``KeyError: 'metadata'`` 예외가 발생할 것입니다.

.. code-block:: python
   :linenos:

   # 의존 라이브러리 : pip install -U openai langchain scikit-learn numpy

   import pickle
   from pathlib import Path
   from pprint import pprint
   from typing import List

   import numpy as np
   import openai
   from environ import Env
   from langchain_community.utils.math import cosine_similarity
   from langchain_core.documents import Document


   env = Env()
   env.read_env()  # .env 파일을 환경변수로서 로딩


   client = openai.Client()


   def print_prices(input_tokens: int, output_tokens: int) -> None:
       input_price = (input_tokens * 0.150 / 1_000_000) * 1_500
       output_price = (output_tokens * 0.600 / 1_000_000) * 1_500
       print("input: tokens {}, krw {:.4f}".format(input_tokens, input_price))
       print("output: tokens {}, krw {:4f}".format(output_tokens, output_price))


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
               response = client.embeddings.create(
                   model=cls.embedding_model,
                   input=doc.page_content,
               )
               vector_store.append(
                   {
                       "document": doc.model_copy(),
                       "embedding": response.data[0].embedding,
                   }
               )

           return vector_store

       def save(self, vector_store_path: Path) -> None:
           """
           벡터 스토어 문서/임베딩 데이터를 지정 경로에 파일로 저장
           """
           with vector_store_path.open("wb") as f:
               # 리스트(self)를 pickle 포맷으로 파일(f)에 저장
               pickle.dump(self, f)

       @classmethod
       def load(cls, vector_store_path: Path) -> "VectorStore":
           """
           지정 경로의 파일을 읽어서 벡터 스토어 문서/임베딩 데이터 복원
           """
           with vector_store_path.open("rb") as f:
               # pickle 포맷으로 파일(f)에서 리스트(VectorStore)를 로딩
               return pickle.load(f)

       def search(self, question: str, k: int = 4) -> List[Document]:
           """
           질의 문자열을 받아서, 벡터 스토어에서 유사 문서를 최대 k개 반환
           """

           # 질문 문자열을 임베딩 벡터 배열로 변환
           response = client.embeddings.create(
               model=self.embedding_model,
               input=question,
           )
           question_embedding = response.data[0].embedding  # 1536 차원, float 배열

           # VectorStore 내에 저장된 모든 문자열을 리스트로 추출
           embedding_list = [row["embedding"] for row in self]

           # 모든 데이터와 코사인 유사도 계산
           similarities = cosine_similarity([question_embedding], embedding_list)[0]
           # 유사도가 높은 순으로 정렬하여 k 개 선택
           top_indices = np.argsort(similarities)[::-1][:k]

           # 상위 k 개 문서를 리스트로 반환
           return [
               self[idx]["document"].model_copy()
               for idx in top_indices
           ]

위에서 생성된 VectorStore 클래스를 다음과 같이 활용할 수 있습니다.

.. code-block:: python
   :linenos:

   def main():
       vector_store_path = Path("vector_store.pickle")

       # 첫번째 실행에서는 vector_store.pickle 파일이 없으므로 load, split, make, save 순서로 데이터를 생성하고 저장합니다.
       if not vector_store_path.is_file():
           doc_list = load()
           print(f"loaded {len(doc_list)} documents")
           doc_list = split(doc_list)
           print(f"split into {len(doc_list)} documents")
           vector_store = VectorStore.make(doc_list)
           vector_store.save(vector_store_path)
           print(f"created {len(vector_store)} items in vector store")
       # 이후 실행에서는 vector_store.pickle 파일이 있으므로 load 순서로 데이터를 로딩합니다.
       else:
           vector_store = VectorStore.load(vector_store_path)
           print(f"loaded {len(vector_store)} items in vector store")

       question = "빽다방 카페인이 높은 음료와 가격은?"

       search_doc_list: List[Document] = vector_store.search(question)
       pprint(search_doc_list)

       print("## 지식 ##")
       지식: str = str(search_doc_list)
       print(repr(지식))

       res = client.chat.completions.create(
           messages=[
               {
                   "role": "system",
                   "content": f"넌 AI Assistant. 모르는 건 모른다고 대답.\n\n[[빽다방 메뉴 정보]]\n{지식}",
               },
               {
                   "role": "user",
                   "content": question,
               },
           ],
           model="gpt-4o-mini",
           temperature=0,
       )
       print_prices(res.usage.prompt_tokens, res.usage.completion_tokens)
       ai_message = res.choices[0].message.content

       print("[AI]", ai_message)


   if __name__ == "__main__":
       main()

실행결과는 아래와 같습니다.

.. code-block:: text

   loaded 1 documents
   split into 10 documents
   created 10 items in vector store
   [Document(metadata={'source': '빽다방.txt'}, page_content='5. 빽사이즈 원조커피(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) [주의. 564mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원'),
    Document(metadata={'source': '빽다방.txt'}, page_content='6. 빽사이즈 원조커피 제로슈거(ICED)\n  - 빽다방의 BEST메뉴를 더 크게, 제로슈거로 즐겨보세요 :) [주의. 686mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원'),
    Document(metadata={'source': '빽다방.txt'}, page_content='3. 사라다빵\n  - 빽다방의 대표메뉴 :) 추억의 감자 사라다빵\n  - 가격: 3900원'),
    Document(metadata={'source': '빽다방.txt'}, page_content='2. 바닐라라떼(ICED)\n  - 부드러운 우유와 달콤하고 은은한 바닐라가 조화를 이루는 음료\n  - 가격: 4200원')]
   ## 지식 ##
   "[Document(metadata={'source': '빽다방.txt'}, page_content='5. 빽사이즈 원조커피(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) [주의. 564mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원'), Document(metadata={'source': '빽다방.txt'}, page_content='6. 빽사이즈 원조커피 제로슈거(ICED)\n  - 빽다방의 BEST메뉴를 더 크게, 제로슈거로 즐겨보세요 :) [주의. 686mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원'), Document(metadata={'source': '빽다방.txt'}, page_content='3. 사라다빵\n  - 빽다방의 대표메뉴 :) 추억의 감자 사라다빵\n  - 가격: 3900원'), Document(metadata={'source': '빽다방.txt'}, page_content='2. 바닐라라떼(ICED)\n  - 부드러운 우유와 달콤하고 은은한 바닐라가 조화를 이루는 음료\n  - 가격: 4200원')]"
   input: tokens 360, krw 0.0810
   output: tokens 115, krw 0.103500
   [AI] 빽다방에서 카페인이 높은 음료는 다음과 같습니다:

   1. **빽사이즈 원조커피(ICED)**
      - 카페인: 564mg
      - 가격: 4000원

   2. **빽사이즈 원조커피 제로슈거(ICED)**
      - 카페인: 686mg
      - 가격: 4000원

   이 두 음료는 카페인 함량이 높으니 섭취에 주의하시기 바랍니다.

마무리
------

축하드립니다. RAG 과정을 바닥부터 구현해보셨습니다. 🎉

RAG에 대한 이해가 만들어지셨으니, 이제 :doc:`./langchain` 를 살펴보시면 각각의 동작이 보이고, 더 쉽게 구현할 수 있을 것입니다.