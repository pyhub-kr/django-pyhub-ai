1단계. 지식 변환 (Load)
============================

  원본 데이터를 텍스트로 변환하고, 불필요한 데이터를 제거하고, 검색과 벡터화에 적합한 형태로 정제하는 과정

이 단계에서는 PDF/TXT/HTML 등의 문서 포맷에 맞는 라이브러리를 사용하여, 문서를 열고 메타 데이터와 내용을 읽어서 텍스트로 변환하신 후에,
``List[Document]`` 객체로 변환하는 단계입니다.

.. admonition:: 랭체인 공식문서 `문서 로더 <https://python.langchain.com/docs/how_to/#document-loaders>`_

   랭체인에서는 다양한 포맷의 파일들에 대해서 일관된 인터페이스로 파이썬 객체로 변환하는 기능을 제공해줍니다. 이를 ``Document Loader`` 라고 합니다.

   * `PDF <https://python.langchain.com/docs/how_to/document_loader_pdf/>`_
   * `웹페이지 <https://python.langchain.com/docs/how_to/document_loader_web/>`_
   * `CSV <https://python.langchain.com/docs/how_to/document_loader_csv/>`_
   * `로컬 파일 <https://python.langchain.com/docs/how_to/document_loader_directory/>`_
   * `HTML 데이터 <https://python.langchain.com/docs/how_to/document_loader_html/>`_
   * `JSON 데이터 <https://python.langchain.com/docs/how_to/document_loader_json/>`_
   * `마크다운 데이터 <https://python.langchain.com/docs/how_to/document_loader_markdown/>`_
   * `마이크로소프트 오피스 데이터 <https://python.langchain.com/docs/how_to/document_loader_office_file/>`_
   * `커스텀 문서 로더 <https://python.langchain.com/docs/how_to/document_loader_custom/>`_


필요성
------

원본 파일은 그대로 검색에 사용할 수 없으며, RAG 시스템이 이해할 수 있는 형태 (텍스트)로 변환하는 과정이 필요합니다.
변환 과정에서 구조적인 노이즈, 형식, 특수문자 등을 제거할 수도 있습니다.

* PDF의 불필요한 메타 데이터, 머릿말/꼬릿말, 웹페이지 내 광고 등


파이썬 구현
----------------

.. admonition:: 빽다방.txt
   :class: dropdown

   .. code-block:: text

    1. 아이스티샷추가(아.샷.추)
      - SNS에서 더 유명한 꿀팁 조합 음료 :) 상콤달콤한 복숭아맛 아이스티에 진한 에스프레소 샷이 어우러져 환상조합
      - 가격: 3800원

    2. 바닐라라떼(ICED)
      - 부드러운 우유와 달콤하고 은은한 바닐라가 조화를 이루는 음료
      - 가격: 4200원

    3. 사라다빵
      - 빽다방의 대표메뉴 :) 추억의 감자 사라다빵
      - 가격: 3900원

    4. 빽사이즈 아메리카노(ICED)
      - 에스프레소 4샷이 들어가 깊고 진한 맛의 아메리카노
      - 가격: 3500원

    5. 빽사이즈 원조커피(ICED)
      - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) [주의. 564mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]
      - 가격: 4000원

    6. 빽사이즈 원조커피 제로슈거(ICED)
      - 빽다방의 BEST메뉴를 더 크게, 제로슈거로 즐겨보세요 :) [주의. 686mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]
      - 가격: 4000원

    7. 빽사이즈 달콤아이스티(ICED)
      - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) 시원한 복숭아맛 아이스티
      - 가격: 4300원

    8. 빽사이즈 아이스티샷추가(ICED)
      - SNS에서 더 유명한 꿀팁 조합 음료 :) 상콤달콤한 복숭아맛 아이스티에 진한 에스프레소 2샷이 어우러져 환상조합
      - 가격: 4800원

    9. 빽사이즈 아이스티 망고추가+노란빨대
      - SNS핫메뉴 아이스티에 망고를 한가득:)
      - 가격: 6300원

    10. 빽사이즈 초코라떼(ICED)
      - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) 진짜~완~전 진한 초코라떼
      - 가격 : 5500원

``빽다방.txt`` 파일을 ``List[Document]`` 객체로 변환하는 2가지 버전의 코드입니다.

.. tab-set::

   .. tab-item:: 파이썬 코드로 직접 문서 변환

      .. code-block:: python
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

   .. tab-item:: 랭체인을 활용해서 문서 변환

      .. code-block:: python
         :linenos:
         :emphasize-lines: 5-7,11-13

         from typing import List
         from pprint import pprint
         from langchain_core.documents import Document

         # 예전에는 `langchain` 라이브러리 기본에서 다양한 `Loader`를 지원했지만,
         # 요즘은 `langchain-community` 라이브러리 등 외부 라이브러리로 지원하는 경우가 많습니다.
         from langchain_community.document_loaders import TextLoader

         # 앞선 "파이썬 코드로 직접 문서 변환" 코드와 동일한 동작
         def load() -> List[Document]:
             file_path = "빽다방.txt"
             loader = TextLoader(file_path=file_path)
             docs: List[Document] = loader.load()
             return docs

         doc_list = load()
         print(f"loaded {len(doc_list)} documents")
         pprint(doc_list)

두 코드 모두 동일한 출력을 반환합니다.

.. code-block:: text

   loaded 1 documents
   [Document(metadata={'source': '빽다방.txt'}, page_content='1. 아이스티샷추가(아.샷.추)\n  - SNS에서 더 유명한 꿀팁 조합 음료 :) 상콤달콤한 복숭아맛 아이스티에 진한 에스프레소 샷이 어우러져 환상조합\n  - 가격: 3800원\n\n2. 바닐라라떼(ICED)\n  - 부드러운 우유와 달콤하고 은은한 바닐라가 조화를 이루는 음료\n  - 가격: 4200원\n\n3. 사라다빵\n  - 빽다방의 대표메뉴 :) 추억의 감자 사라다빵\n  - 가격: 3900원\n\n4. 빽사이즈 아메리카노(ICED)\n  - 에스프레소 4샷이 들어가 깊고 진한 맛의 아메리카노\n  - 가격: 3500원\n\n5. 빽사이즈 원조커피(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) [주의. 564mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원\n\n6. 빽사이즈 원조커피 제로슈거(ICED)\n  - 빽다방의 BEST메뉴를 더 크게, 제로슈거로 즐겨보세요 :) [주의. 686mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\n  - 가격: 4000원\n\n7. 빽사이즈 달콤아이스티(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) 시원한 복숭아맛 아이스티\n  - 가격: 4300원\n\n8. 빽사이즈 아이스티샷추가(ICED)\n  - SNS에서 더 유명한 꿀팁 조합 음료 :) 상콤달콤한 복숭아맛 아이스티에 진한 에스프레소 2샷이 어우러져 환상조합\n  - 가격: 4800원\n\n9. 빽사이즈 아이스티 망고추가+노란빨대\n  - SNS핫메뉴 아이스티에 망고를 한가득:)\n  - 가격: 6300원\n\n10. 빽사이즈 초코라떼(ICED)\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) 진짜~완~전 진한 초코라떼\n  - 가격 : 5500원\n')]

.. admonition:: Tip. ``.metadata`` 속성에는 어떤 메타 데이터도 저장할 수 있습니다.
   :class: tip

   ``.metadata`` 속성 값은 프롬프트에 문자열로서 ``"{'source': '빽다방.txt'}"`` 형태로 전달됩니다.
   타입이 정해져있지 않기에, 어떤 이름의 키나 어떤 타입의 값이든 다양한 메타정보를 저장하실 수 있습니다.
   문서와 관련된 정보라면 어떤 정보든 저장하실 수 있습니다.
   문서 내용에서 핵심 키워드를 뽑아서 ``keywords`` 키로 저장하거나, 요약을 ``summary`` 키로 저장하기도 합니다.
   PDF Loader 경우에도 PDF Loader 종류에 따라 설정해주는 메타 데이터가 다릅니다.


정리
-----

RAG 에서는 질문과 유사한 문서를 문서 단위로 찾아서, 프롬프트에 적용합니다.
각 문서는 아래 조건을 맞춰주시면 보다 좋은 RAG 결과를 얻을 수 있습니다.

1. 한 문서에 여러 주제가 섞여 있지 않고, 단일 핵심 정보를 적절한 크기로 포함할 것

   * 불필요한 정보까지 함께 제공하게 됩니다.
   * 문서의 내용이 너무 짧거나 부족하면, 여러 문서를 검색해야 하므로 RAG 성능이 저하됩니다.

2. 일정한 구조를 유지할 것

3. 관련없는 정보를 제거할 것

4. 다른 문서와 중복되지 않도록 구성할 것

5. 적절한 메타 데이터를 포함할 것


.. admonition:: Tip. 보다 좋은 RAG 결과를 얻기 위해서는, 원본 지식 데이터의 품질을 관리하는 것이 중요합니다.
   :class: tip

   원본 지식 데이터를 처리할 때, 단순히 파일 내용을 텍스트로 변환하는 것만으로는 충분하지 않을 수 있습니다.
   랭체인(LangChain)을 사용하든 직접 구현하든, 변환된 텍스트 문서가 효과적으로 검색되고 활용될 수 있도록 구조화하고 최적화하여,
   **원본 지식 데이터의 품질을 관리하는 것** 이 중요합니다.

   하지만, 원본 지식 데이터가 방대할 경우 각 문서의 내용을 일일이 조정하고 검수하는 것은 어려울 수 있겠죠. 😢


.. admonition:: 참고. [테디노트] R.A.G. 우리가 절대 쉽게 결과물을 얻을 수 없는 이유

   https://www.youtube.com/watch?v=NfQrRQmDrcc
