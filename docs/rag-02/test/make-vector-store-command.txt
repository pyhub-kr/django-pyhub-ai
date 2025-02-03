==============================
make_vector_store 명령 수정
==============================


PaikdabangMenuDocument 모델을 통한 저장
==============================================

앞서 구현했던 ``make_vector_store`` 명령을 수정하여,
파이썬 리스트를 생성하고 pickle 포맷으로 저장하는 대신
``PaikdabangMenuDocument`` 모델을 통해 저장토록 합니다.

진행 상황은 ``tqdm`` 라이브러리를 통해 표시하겠습니다. 라이브러리가 설치되어있지 않다면
``uv run pip install --upgrade tqdm`` 명령으로 설치해주세요.

.. code-block:: python
    :caption: ``chat/management/commands/make_vector_store.py``
    :linenos:
    :emphasize-lines: 3,5,8,27-28,30-36

    from pathlib import Path

    # from django.conf import settings
    from django.core.management import BaseCommand
    from tqdm import tqdm

    from chat import rag
    from chat.models import PaikdabangMenuDocument


    class Command(BaseCommand):
        def add_arguments(self, parser):
            parser.add_argument(
                "txt_file_path",
                type=str,
                help="VectorStore로 저장할 원본 텍스트 파일 경로",
            )

        def handle(self, *args, **options):
            txt_file_path = Path(options["txt_file_path"])

            doc_list = rag.load(txt_file_path)
            print(f"loaded {len(doc_list)} documents")
            doc_list = rag.split(doc_list)
            print(f"split into {len(doc_list)} documents")

            # vector_store = rag.VectorStore.make(doc_list)
            # vector_store.save(settings.VECTOR_STORE_PATH)

            # 문서 목록을 순회하며, 모델 인스턴스를 생성하고 저장합니다.
            for doc in tqdm(doc_list):
                paikdabang_menu_document = PaikdabangMenuDocument(
                    page_content=doc.page_content,
                    metadata=doc.metadata,
                )
                paikdabang_menu_document.save()


실행하면 다음과 같이 진행 상황이 표시되구요.

.. code-block:: text
    :emphasize-lines: 1

    $ python manage.py make_vector_store ./chat/assets/빽다방.txt
    [2025-01-29 14:40:09,940] Loaded vector store 10 items
    loaded 1 documents
    split into 10 documents
    100%|███████████████████████████| 10/10 [00:06<00:00,  1.66it/s]

데이터베이스의 ``chat_paikdabangmenudocument`` 테이블을 조회하면, 임베딩 데이터가 자동으로 생성된 것을 확인하실 수 있습니다.

.. figure:: ./assets/supabase-table-embedding.png


개선 포인트
==============

현재 코드는 각 ``PaikdabangMenuDocument`` 인스턴스마다 개별적으로 OpenAI Embedding API를 호출하고,
개별적으로 데이터베이스에 저장하고 있습니다. 이로 인해 다음과 같은 비효율이 발생합니다.

1. 비효율적인 데이터베이스 삽입

   - 각 문서마다 개별적으로 INSERT 쿼리를 실행하기보다, 여러 개의 INSERT 쿼리를 하나의 배치로 묶어 실행하면
     트랜잭션 오버헤드를 줄이고 성능을 최적화할 수 있습니다.

2. API 호출 횟수 증가

   - 각 문서마다 개별적으로 Embedding API를 호출하기에 네트워크 요청이 과도하게 발생합니다.
     여러 개의 문서를 한 번의 API 요청으로 처리하면 전체 처리 시간을 단축할 수 있습니다.
