4단계. 지식 저장 (Store)
========================

    벡터화된 데이터를 효율적으로 관리하고 검색할 수 있도록 저장하는 과정


.. raw:: html

    <div class="video-container">
        <iframe
            src="https://www.youtube.com/embed/9ayknWI-VcI?start=2742"
            frameborder="0"
            allowfullscreen>
        </iframe>
    </div>

    <small>본 페이지는 45:42 지점부터 59:33 지점까지 보시면 됩니다.</small>


필요성
---------

단순히 문서를 벡터로 변환했다고 해서 즉시 활용할 수 있는 것이 아니라, 빠르고 정확한 검색이 가능하도록 저장해야 하며, 적절한 인덱싱 기법을 적용하여 검색 속도를 최적화해야만 합니다.
"지식 저장 (Store)" 단계는 효율적인 검색을 위한 최적화된 저장소 구축 과정입니다.

본 튜토리얼에서는 파이썬 코드로 저장만 구현하고 인덱싱 과정은 다루지 않습니다.
Vector Store를 사용하실 때 인덱싱 기능을 활용하실 수 있습니다.


파이썬 구현
----------------

본 튜토리얼에서는 비효율적인 방식이지만 벡터 데이터를 리스트에 저장하고 이를 ``pickle`` 포맷으로 파일로 저장하는 방식으로 간략히 구현하여,
Vector Store의 동작을 이해해보겠습니다.

``list`` 클래스를 상속받은 ``VectorStore`` 클래스를 구현하여 ``VectorStore`` 내에서 벡터 데이터를 저장하고 관리할 수 있도록 구현합니다.
다음 4개의 메서드를 지원합니다.

#. ``make`` 메서드 : 문서 리스트를 받아서 벡터 데이터 리스트를 생성 (``Embed`` 단계)
#. ``save`` 메서드 : 현재의 벡터 데이터 리스트를 디스크에 파일로 저장
#. ``load`` 메서드 : 디스크에 저장된 벡터 데이터를 로딩하여 리스트 화
#. ``search`` 메서드 : 질문 문자열을 받아서 유사 문서 목록을 검색

``embed`` 함수를 ``make`` 메서드로 리팩토링
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

먼저 :doc:`./03-embed` 단계에서 구현한 ``embed`` 함수를 ``VectorStore.make`` 클래스 함수로 리팩토링합니다.

.. code-block:: python
   :linenos:

   class VectorStore(list):
       # 지식에 사용한 임베딩 모델과 질문에 사용할 임베딩 모델은 동일해야만 합니다.
       # 각각 임베딩 모델명을 지정하지 않고, 임베딩 모델명을 클래스 변수로 선언하여
       # 모델명 변경의 용이성을 확보합니다.
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

        # TODO: 이어서 구현할 예정입니다.

        # 벡터 스토어 문서/임베딩 데이터를 지정 경로에 파일로 저장
        # def save(self, vector_store_path: Path) -> None: ...

        # 지정 경로의 파일을 읽어서 벡터 스토어 문서/임베딩 데이터 복원
        # @classmethod
        # def load(cls, vector_store_path: Path) -> "VectorStore": ...

        # 질의 문자열을 받아서, 벡터 스토어에서 유사 문서를 최대 k개 반환
        # def search(self, question: str, k: int = 4) -> List[Document]:


   # vector_store = embed(doc_list)
   vector_store = VectorStore.make(doc_list)


``save`` 메서드와 ``load`` 메서드 구현
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

벡터 데이터가 메모리에만 저장되어있는 상황이기에 프로세스가 종료되면 데이터가 사라집니다. 따라서 데이터를 디스크에 저장하고 관리할 필요가 있습니다.

파이썬 객체를 파일로 저장하는 가장 간단한 방법으로서 `pickle이 파이썬 기본에서 지원 <https://docs.python.org/ko/3.13/library/pickle.html>`_ 됩니다.
물론 JSON이나 CSV 등 다양한 포맷으로 저장할 수 있습니다. 물론 벡터 데이터를 저장하는 효율적인 방법은 아니지만, 구현이 간단합니다.

.. code-block:: python
   :linenos:

   import pickle
   from pathlib import Path

   class VectorStore(list):
       # ...

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

        # TODO: 이어서 구현할 예정입니다.

        # 질의 문자열을 받아서, 벡터 스토어에서 유사 문서를 최대 k개 반환
        # def search(self, question: str, k: int = 4) -> List[Document]:


``search`` 메서드 구현
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``VectoreStore`` 클래스에 지식 검색을 위한 ``search`` 메서드는 :doc:`./05-search` 단계에서 구현하겠습니다.


``VectorStore`` 클래스 현재 상황
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
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
       
        # TODO: 이어서 구현할 예정입니다.

        # 질의 문자열을 받아서, 벡터 스토어에서 유사 문서를 최대 k개 반환
        # def search(self, question: str, k: int = 4) -> List[Document]:


위 ``VectorStore`` 클래스는 다음과 같이 활용할 수 있습니다.

.. code-block:: python
   :linenos:

   def main():
       vector_store_path = Path("vector_store.pickle")

       # 지정 경로에 파일이 없으면
       # 문서를 로딩하고 분할하여 벡터 데이터를 생성하고 해당 경로에 저장합니다.
       if not vector_store_path.is_file():
           doc_list = load()
           print(f"loaded {len(doc_list)} documents")
           doc_list = split(doc_list)
           print(f"split into {len(doc_list)} documents")
           vector_store = VectorStore.make(doc_list)
           vector_store.save(vector_store_path)
           print(f"created {len(vector_store)} items in vector store")
        # 지정 경로에 파일이 있으면, 로딩하여 VectorStore 객체를 복원합니다.
       else:
           vector_store = VectorStore.load(vector_store_path)
           print(f"loaded {len(vector_store)} items in vector store")

       # TODO: RAG를 통해 지식에 기반한 AI 답변을 구해보겠습니다.
       question = "빽다방 카페인이 높은 음료와 가격은?"
       print(f"RAG를 통해 '{question}' 질문에 대해서 지식에 기반한 AI 답변을 구해보겠습니다.")


   if __name__ == "__main__":
       main()

#. 첫번째 실행에서는 ``vector_store.pickle`` 파일이 없으므로 ``load``, ``split``, ``make``, ``save`` 순서로 호출되어, ``VectoreStore`` 객체를 생성하고 파일로 백업합니다.
#. 이후 실행에서는 ``vector_store.pickle`` 파일이 있으므로 ``load`` 함수를 호출하여, ``VectorStore`` 객체를 복원합니다.
#. 재생성하실려면 ``vector_store.pickle`` 파일을 삭제하고 다시 실행해주세요.

.. admonition:: 참고: batch API를 활용해서 임베딩 비용을 50% 절감하실 수 있습니다.
   :class: tip

   임베딩 API를 활용하면 즉시 임베딩 처리가 가능합니다. 그러나 대부분의 문서 임베딩 작업은 실시간 처리가 아닌 대량 데이터를 천천히 처리해도 문제가 없는 경우가 많습니다.
   이런 경우 Batch API를 활용하면 비용을 크게 절감할 수 있습니다.

   `OpenAI 가격 <https://openai.com/api/pricing/>`_ 페이지에 따르면 Batch 방식을 사용할 경우 비용이 실시간 처리 방식 대비 **50% 저렴** 합니다.
