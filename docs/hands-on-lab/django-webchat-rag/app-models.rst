========================================
🪜 장고 문서 모델 생성 및 마이그레이션
========================================


.. admonition:: `관련 커밋 <https://github.com/pyhub-kr/django-webchat-rag-langcon2025/commit/73f88f1c792f1d49a136046e228707ce404dc105>`_
   :class: dropdown

   * 변경 파일을 한 번에 덮어쓰기 하실려면, :doc:`/utils/pyhub-git-commit-apply` 설치하신 후에, 프로젝트 루트에서 아래 명령 실행하시면
     지정 커밋의 모든 파일을 다운받아 현재 경로에 덮어쓰기합니다.

   .. code-block:: bash

      python -m pyhub_git_commit_apply https://github.com/pyhub-kr/django-webchat-rag-langcon2025/commit/73f88f1c792f1d49a136046e228707ce404dc105

   ``uv``\를 사용하실 경우 

   .. code-block:: bash

      uv run pyhub-git-commit-apply https://github.com/pyhub-kr/django-webchat-rag-langcon2025/commit/73f88f1c792f1d49a136046e228707ce404dc105


장고 앱 생성 및 등록
=======================

``chat`` 앱을 생성합니다.

.. code-block:: shell

    python manage.py startapp chat

``chat/urls.py`` 파일을 아래 내용으로 생성합니다.

.. code-block:: python
    :caption: ``chat/urls.py``

    from django.urls import path
    from . import views

    urlpatterns = []

``mysite/urls.py`` 파일에 ``chat/urls.py`` 패턴을 포함시키고,
루트 URL 요청은 ``chat/`` 주소로 이동시키겠습니다.

.. code-block:: python
    :caption: ``mysite/urls.py`` 덮어쓰기
    :emphasize-lines: 4,8-9
    :linenos:

    from django.apps import apps
    from django.contrib import admin
    from django.urls import include, path
    from django.views.generic import RedirectView

    urlpatterns = [
        path("admin/", admin.site.urls),
        path("chat/", include("chat.urls")),
        path("", RedirectView.as_view(url="/chat/")),
    ]


    if apps.is_installed("debug_toolbar"):
        urlpatterns = [
            path("__debug__/", include("debug_toolbar.urls")),
        ] + urlpatterns


``chat`` 앱을 프로젝트에 등록하여 활성화합니다.

.. code-block:: python
    :caption: ``mysite/settings.py``
    :emphasize-lines: 4

    INSTALLED_APPS = [
        # ...
        'pyhub.rag',
        'chat',
    ]


세법 해석례 문서 모델 생성
===============================

``django-pyhub-rag`` 라이브러리에서는 2개의 추상화 문서 모델을 지원합니다.

* ``SQLiteVectorDocument`` 추상화 모델 : ``sqlite-vec`` 확장 백엔드
* ``PGVectorDocument`` 추상화 모델 : ``pgvector`` 확장 백엔드

두 추상화 문서 모델은 모두 디폴트로 1536 차원 ``embedding`` 필드를 가지며 ``text-embedding-3-small`` 임베딩 모델을 사용합니다.

.. tab-set::

    .. tab-item:: sqlite

        .. code-block:: python
            :caption: ``chat/models.py``
            :linenos:

            from pyhub.rag.models.sqlite import SQLiteVectorDocument

            class TaxLawDocument(SQLiteVectorDocument):
                pass

    .. tab-item:: postgres

        .. code-block:: python
            :caption: ``chat/models.py``
            :linenos:

            from pyhub.rag.models.postgres import PGVectorDocument

            class TaxLawDocument(PGVectorDocument):
                class Meta:
                    indexes = [
                        PGVectorDocument.make_hnsw_index(
                            "chat_taxlawdoc_idx",  # 데이터베이스 내에서 유일한 이름으로 지정하셔야 합니다.
                            # "vector",            # field type
                            # "cosine",            # distance metric
                        ),
                    ]

인덱스를 지정하면 유사 문서 검색 속도를 향상시킬 수 있습니다.

* ``sqlite-vec`` 확장에서는 별도 인덱스 설정은 없고 테이블 생성 시에 ``distance_metric=cosine`` 옵션을 지정합니다.
* ``pgvector`` 확장에서는 인덱스를 지원하므로, Cosine Distance 등 거리 검색에 사용하실 인덱스를 지정해주세요.

.. admonition:: ``pgvector``\에서 지원하는 인덱스 타입
    :class: tip

    :doc:`/rag-02/index` 튜토리얼의 :doc:`/rag-02/pgvector-model` 문서를 참고하세요.

만약 2000 차원을 초과한 임베딩이 필요한 경우 ``embedding`` 필드를 재정의하고, ``text-embedding-3-large`` 임베딩 모델을 사용합니다.

.. tab-set::

    .. tab-item:: sqlite

        ``sqlite-vec``\에서는 인덱스 지정이 없고, 테이블 생성 시에 ``distance_metric=cosine`` 옵션을 지정합니다.

        .. code-block:: python
            :caption: ``chat/models.py``
            :emphasize-lines: 1,5-9
            :linenos:

            from pyhub.rag.fields.sqlite import SQLiteVectorField
            from pyhub.rag.models.sqlite import SQLiteVectorDocument

            class TaxLawDocument(SQLiteVectorDocument):
                embedding = SQLiteVectorField(
                    dimensions=3072,
                    editable=False,
                    embedding_model="text-embedding-3-large",
                )

    .. tab-item:: postgres

        ``PGVectorField`` 내부에서는 2000차원 이하에서는 ``vector`` 타입으로 생성되고, 2000차원을 초과할 경우 ``halfvec`` 타입으로 생성됩니다.
        인덱스 타입도 필드 타입에 맞게 지정해셔야만 합니다.

        .. code-block:: python
            :caption: ``chat/models.py``
            :emphasize-lines: 1,5-9,15
            :linenos:

            from pyhub.rag.fields.postgres import PGVectorField
            from pyhub.rag.models.postgres import PGVectorDocument

            class TaxLawDocument(PGVectorDocument):
                embedding = PGVectorField(
                    dimensions=3072,
                    editable=False,
                    embedding_model="text-embedding-3-large",
                )

                class Meta:
                    indexes = [
                        PGVectorDocument.make_hnsw_index(
                            "chat_taxlawdoc_idx",
                            "halfvec",  # 2000차원 초과 시에는 halfvec 타입
                            "cosine",   # 거리 검색에 사용하실 인덱스 타입
                        ),
                    ]

준비한 세법 해석례 데이터는 3072 차원 임베딩을 가지고 있으므로, 위 코드처럼 ``embedding`` 필드를 재정의하여 3072 차원 임베딩을 생성합니다.

.. warning::

    ``SQLiteVectorDocument`` 모델과 ``PGVectorDocument`` 모델은 거의 동일한 코드이지만,
    마이그레이션 내역이 다르기 때문에 데이터베이스를 변경할 경우 마이그레이션 파일을 다시 생성하셔야 합니다.


마이그레이션
===============================

마이그레이션 파일을 생성하고 (작업 지시어 작성), 수행될 SQL 문을 확인하고 (작업 내역 확인), 마이그레이션을 수행합니다 (작업 수행).

.. code-block:: shell

    python manage.py makemigrations chat
    python manage.py sqlmigrate chat 0001_initial
    python manage.py migrate

.. tab-set::

    .. tab-item:: sqlite

        .. figure:: ./assets/app-models/0001-migrate-sqlite.png

        테이블 생성 시에 ``CREATE VIRTUAL TABLE`` 쿼리로 가상 테이블이 생성됨을 확인하실 수 있고,
        ``embedding`` 필드를 ``float[3072]`` 타입으로 차원수에 맞게 생성됨을 확인하실 수 있습니다.

    .. tab-item:: postgres

        .. TODO: 윈도우에서 pgvector 스샷을 다시 떠서, 위 SQLite 스타일로 적용하기

        .. figure:: ./assets/app-models/0001-migrate-postgres.png

        ``embedding`` 필드는 3072차원으로서 2000차원이 넘기에 ``halfvec`` 타입으로 생성됩니다.
        2000차원 이하는 ``vector`` 타입을 사용할 수 있습니다.
