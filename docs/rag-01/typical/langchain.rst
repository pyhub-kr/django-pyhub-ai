전형적인 RAG (랭체인 버전)
==================================

.. admonition:: 랭체인 버전은 다음 튜토리얼에서 진행하겠습니다.
   :class: attention

   많은 응원 부탁드립니다. 😉

지식 Load 및 Split
-----------------------------

.. code-block:: bash
   :caption: 의존 라이브러리 설치

   pip install -U langchain langchain-community langchain-text-splitters

.. code-block:: python
   :linenos:

   from pprint import pprint

   from langchain_community.document_loaders import TextLoader
   from langchain_text_splitters import RecursiveCharacterTextSplitter

   # Load 단계
   doc_list = TextLoader(file_path="./빽다방.txt").load()
   print(f"loaded {len(doc_list)} documents")  # 1

   # Split 단계
   text_splitter = RecursiveCharacterTextSplitter(
       chunk_size=140,  # 문서를 나눌 최소 글자 수 (디폴트: 4000)
       chunk_overlap=0,  # 문서를 나눌 때 겹치는 글자 수 (디폴트: 200)
   )
   doc_list = text_splitter.split_documents(doc_list)
   print(f"split into {len(doc_list)} documents")  # 9

   pprint(doc_list)

``RecursiveCharacterTextSplitter`` 에서는 구분자 (디폴트 ``["\n\n", "\n", " ", ""]``)로 나누고
``chunk_size`` 크기 만큼 문서를 모으고, 이어지는 문서는 ``chunk_overlap`` 만큼 겹쳐서 문서를 생성합니다.

"빽다방.txt" 파일에서 각 메뉴들이 구분자 ``\n\n``\로 나눠지니까 10개 문서로 나눠지지만,
각 문서의 길이가 ``[98, 68, 52, 68, 114, 126, 81, 105, 65, 83]`` 이고,
두번째 문서는 68자, 세번째 문서는 52자로서 ``chunk_size=140`` 보다 작은 값이라 한 문서로 묶여 처리되었습니다.

그래서 10개의 문서가 아니라, 9개의 문서로만 나눠진 상황입니다. 2번 메뉴와 3번 메뉴가 묶여있네요. 🤔

.. code-block:: text
   :emphasize-lines: 4

   loaded 1 documents
   split into 9 documents
   [Document(metadata={'source': './빽다방.txt'}, page_content='1. 아이스티샷추가(아.샷.추)\n  - SNS에서 더 유명한 꿀팁 조합 음료 :) 상콤달콤한 복숭아맛 아이스티에 진한 에스프레소 샷이 어우러져 환상조합\n  - 가격: 3800원'),
    Document(metadata={'source': './빽다방.txt'}, page_content='2. 바닐라라떼(ICED)\n  - 부드러운 우유와 달콤하고 은은한 바닐라가 조화를 이루는 음료\n  - 가격: 4200원\n\n3. 사라다빵\n  - 빽다방의 대표메뉴 :) 추억의 감자 사라다빵\n  - 가격: 3900원'),
    Document(metadata={'source': './빽다방.txt'}, page_content='4. 빽사이즈 아메리카노(ICED)\n  - 에스프레소 4샷이 들어가 깊고 진한 맛의 아메리카노\n  - 가격: 3500원'),
    Document(metadata={'source': './빽다방.txt'}, page_content='5. 빽사이즈 원조커피(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) [주의. 564mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원'),
    Document(metadata={'source': './빽다방.txt'}, page_content='6. 빽사이즈 원조커피 제로슈거(ICED)\n  - 빽다방의 BEST메뉴를 더 크게, 제로슈거로 즐겨보세요 :) [주의. 686mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원'),
    Document(metadata={'source': './빽다방.txt'}, page_content='7. 빽사이즈 달콤아이스티(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) 시원한 복숭아맛 아이스티\n  - 가격: 4300원'),
    Document(metadata={'source': './빽다방.txt'}, page_content='8. 빽사이즈 아이스티샷추가(ICED)\n  - SNS에서 더 유명한 꿀팁 조합 음료 :) 상콤달콤한 복숭아맛 아이스티에 진한 에스프레소 2샷이 어우러져 환상조합\n  - 가격: 4800원'),
    Document(metadata={'source': './빽다방.txt'}, page_content='9. 빽사이즈 아이스티 망고추가+노란빨대\n  - SNS핫메뉴 아이스티에 망고를 한가득:)\n  - 가격: 6300원'),
    Document(metadata={'source': './빽다방.txt'}, page_content='10. 빽사이즈 초코라떼(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) 진짜~완~전 진한 초코라떼\n  - 가격 : 5500원')]

전체 코드
-------------------

VectorStore는 `FAISS <https://python.langchain.com/docs/integrations/vectorstores/faiss/>`_\를 사용하겠습니다.
Facebook AI Research에서 개발한 효율적인 유사도 검색 라이브러리입니다.
대규모 데이터셋에서도 빠른 유사도 검색이 가능하며, 메모리에 데이터를 저장하고 디스크에 저장/로드할 수 있습니다.

.. code-block:: bash
   :caption: 의존 라이브러리 설치

   pip install -U langchain langchain-community langchain-openai langchain-text-splitters faiss-cpu tiktoken

.. code-block:: python
   :linenos:

   import os.path
   from pprint import pprint
   from typing import List
   from uuid import uuid4

   import faiss
   from langchain.chains.llm import LLMChain
   from langchain.chains.retrieval_qa.base import RetrievalQA
   from langchain_community.docstore import InMemoryDocstore
   from langchain_community.document_loaders import TextLoader
   from langchain_core.messages import AIMessage
   from langchain_core.prompts import PromptTemplate
   from langchain_core.runnables import RunnableLambda
   from langchain_core.vectorstores import VectorStore
   from langchain_openai import ChatOpenAI
   from langchain_openai.embeddings import OpenAIEmbeddings
   from langchain_community.vectorstores import FAISS
   from langchain_text_splitters import RecursiveCharacterTextSplitter

   faiss_folder_path = "faiss_index"

   embedding = OpenAIEmbeddings(model="text-embedding-3-small")


   def get_vector_store() -> VectorStore:
       if not os.path.exists(faiss_folder_path):
           doc_list = TextLoader(file_path="./빽다방.txt").load()
           print(f"loaded {len(doc_list)} documents")  # 1

           text_splitter = RecursiveCharacterTextSplitter(
               chunk_size=140,
               chunk_overlap=0,
               length_function=len,
               is_separator_regex=True,
           )
           doc_list = text_splitter.split_documents(doc_list)
           print(f"split into {len(doc_list)} documents")  # 9

           차원수 = len(embedding.embed_query("hello"))  # 1536
           # 차원수 = 1536

           index = faiss.IndexFlatL2(차원수)

           vector_store = FAISS(
               embedding_function=embedding,
               index=index,
               docstore=InMemoryDocstore(),
               index_to_docstore_id={},
           )

           uuids = [str(uuid4()) for _ in range(len(doc_list))]
           vector_store.add_documents(documents=doc_list, ids=uuids)

           vector_store.save_local("faiss_index")
       else:
           vector_store = FAISS.load_local(
               faiss_folder_path,
               embedding,
               allow_dangerous_deserialization=True,
           )

       return vector_store


   def main():
       vector_store = get_vector_store()

       question = "빽다방 카페인이 높은 음료와 가격은?"

       # 직접 similarity_search 메서드 호출을 통한 유사 문서 검색
       # search_doc_list = vector_store.similarity_search(question)
       # pprint(search_doc_list)

       # retriever 인터페이스를 통한 유사 문서 검색
       # retriever = vector_store.as_retriever()
       # search_doc_list = retriever.invoke(question)
       # pprint(search_doc_list)

       # Chain을 통한 retriever 자동 호출
       # llm = ChatOpenAI(model_name="gpt-4o-mini")
       # retriever = vector_store.as_retriever()
       # qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
       # ai_message = qa_chain.invoke(question)
       # print("[AI]", ai_message["result"])  # keys: "query", "result"

       llm = ChatOpenAI(model_name="gpt-4o-mini")
       retriever = vector_store.as_retriever()
       prompt_template = PromptTemplate(
           template="Context: {context}\n\nQuestion: {question}\n\nAnswer:",
           input_variables=["context", "question"],
       )

       rag_pipeline = (
           RunnableLambda(
               # 아래 invoke를 통해 전달되는 값이 인자로 전달됩니다.
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


   if __name__ == "__main__":
       main()

실행 결과
-----------------

.. code-block:: text

   [AI] 빽다방에서 카페인이 높은 음료와 그 가격은 다음과 같습니다:

   1. **빽사이즈 원조커피(ICED)**  
      - 카페인: 564mg  
      - 가격: 4000원  

   2. **빽사이즈 원조커피 제로슈거(ICED)**  
      - 카페인: 686mg  
      - 가격: 4000원  

   이 두 음료는 카페인 함량이 높으므로, 카페인에 민감한 어린이와 임산부는 섭취에 주의해야 합니다.
   {'input_tokens': 499, 'output_tokens': 132, 'total_tokens': 631, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}}

랭체인/랭그래프 버전도 기대해주세요. 🥳
