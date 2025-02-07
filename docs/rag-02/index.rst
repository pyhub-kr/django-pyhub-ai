=======================================================
RAG #02. 실전: 세법 RAG를 위한 pgvector 임베딩
=======================================================

.. tip::

    곧 유튜브 영상으로 인사드리겠습니다. 😉

지난 :doc:`/rag-01/index` 튜토리얼에서는 RAG에 대한 이해도를 높이기 위해
Vector Store를 파이썬 리스트로 직접 구현했었습니다.
이번 튜토리얼부터 **실전 튜토리얼**\로서, 실제 서비스 개발에 많이 사용되어지는
Postgres `pgvector <https://github.com/pgvector/pgvector>`_ 확장을
장고 프로젝트에 통합하는 방법을 다뤄보겠습니다.

``pgvector``\를 선택한 이유는 다음과 같습니다.

#. Postgres를 사용하는 서비스에서는 추가 인프라 없이 벡터 검색 기능을 구현할 수 있습니다.
#. 장고가 지원하는 수많은 데이터베이스 중에 Postgres는 장고가 가장 잘 지원하는 오픈소스 데이터베이스입니다.
#. 단일 데이터베이스로 관계형 데이터와 벡터 데이터를 함께 관리할 수 있어 운영이 단순해집니다.
   물론 벡터 데이터를 별도의 데이터베이스로 나눠 관리할 수도 있습니다.
   장고 모델의 라우터 기능을 활용하면, 모델 별로 다른 데이터베이스 혹은
   다른 데이터베이스 엔진을 바라보도록 손쉽게 설정할 수 있습니다.
#. ``pgvector`` 파이썬 라이브러리에서 장고 ORM을 직접 지원하기에, 통합이 쉽습니다.

본 튜토리얼을 통해, 장고 모델을 활용하여 Postgres 데이터베이스에 데이터를 저장하고
자동으로 임베딩 벡터까지 생성하여 저장하는 방법을 배우게 됩니다.

.. code-block:: python

    # 문서 데이터만 지정하면, 임베딩까지 자동으로 OK
    PaikdabangMenuDocument.objects.create(
        page_content="1. 아이스티샷추가(아.샷.추)\n  - SNS에서 더 유명한 꿀팁 조합 음료 :) 상콤달콤한 복숭아맛 아이스티에 진한 에스프레소 샷이 어우러져 환상조합\n  - 가격: 3800원",
        metadata={"source": "./chat/assets/빽다방.txt"},
    )

쿼리셋을 통해 손쉽게 코사인 거리 검색을 사용할 수 있습니다. 물론 L2 거리 검색도 가능합니다.
본 튜토리얼에서 ``search`` 메서드를 재사용성 높은 방식으로 직접 구현해봅니다.

.. code-block:: python

    # 일반적인 장고 쿼리셋 사용법과 동일한 방식으로 유사도 검색 지원
    doc_list: List[PaikdabangMenuDocument] = \
        await PaikdabangMenuDocument.objects.search("빽다방 고카페인 음료 종류는?")

``search`` 메서드는 쿼리셋 메서드이기에, 장고 쿼리셋으로 검색 대상의 범위를 좁힌 뒤에
유사 문서 검색을 수행할 수 있습니다.

.. code-block:: python

    qs = PaikdabangMenuDocument.objects.filter(...)  # 조회 조건 지정
    doc_list = await qs.search("빽다방 고카페인 음료 종류는?")

문서 리스트를 프롬프트 문자열에 손쉽게 전달할 수 있습니다.

.. code-block:: python

    # 랭체인 Document 리스트와 동일한 포맷으로 변환됩니다.
    지식 = str(doc_list)

새로운 문서 모델이 필요할 때, 본 튜토리얼을 통해 직접 구현한 :doc:`Document 모델 상속 </rag-02/abstract-document>` 만으로
손쉽게 새로운 문서 모델을 추가할 수 있게 됩니다.

.. code-block:: python

    # 상속 만으로 임베딩부터 유사도 검색까지 OK. (인덱스 지정은 필요합니다.)
    class StarbucksMenuDocument(Document):
        pass

    # 세법 해석례 문서 모델
    class TaxLawDocument(Document):
        pass

``TaxLawDocument`` 모델을 통해 세법 해석례 문서를 저장하고, 아래와 같이 간결한 코드로
질문과 유사한 문서를 검색할 수 있습니다.

.. code-block:: python

    question = "재화 수출하는 경우 영세율 첨부 서류로 수출실적명세서가 없는 경우 해결 방법"
    doc_list = await TaxLawDocument.objects.search(question)

준비되셨나요? 시작합니다. 😉

.. toctree::
    :maxdepth: 1
    :caption: 목차
    :numbered:

    setup
    pgvector
    pgvector-model
    max-token-validator
    django-lifecycle
    make-vector-store-command
    queryset-search
    repr
    bulk-create
    batch
    abstract-document
    taxlaw
    closing
