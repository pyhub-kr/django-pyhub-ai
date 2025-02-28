========================================
🪜 장고 문서 모델 생성 및 마이그레이션
========================================


.. admonition:: `관련 커밋 <https://github.com/pyhub-kr/django-webchat-rag-langcon2025/commit/af069ef93498c5597eee29cbab50cc1ac1a2088f>`_
   :class: dropdown

   * 변경 파일을 한 번에 덮어쓰기 하실려면, :doc:`/utils/pyhub-git-commit-apply` 설치하신 후에, 프로젝트 루트에서 아래 명령 실행하시면
     지정 커밋의 모든 파일을 다운받아 현재 경로에 덮어쓰기합니다.

   .. code-block:: bash

      python -m pyhub_git_commit_apply https://github.com/pyhub-kr/django-webchat-rag-langcon2025/commit/af069ef93498c5597eee29cbab50cc1ac1a2088f

   ``uv``\를 사용하실 경우 

   .. code-block:: bash

      uv run pyhub-git-commit-apply https://github.com/pyhub-kr/django-webchat-rag-langcon2025/commit/af069ef93498c5597eee29cbab50cc1ac1a2088f


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

            from pyhub.rag.models.sqlite import SQLiteVectorDocument

            class TaxLawDocument(SQLiteVectorDocument):
                pass

    .. tab-item:: postgres

        .. code-block:: python
            :caption: ``chat/models.py``

            from pyhub.rag.models.postgres import PGVectorDocument

            class TaxLawDocument(PGVectorDocument):
                pass

``pgvector`` 확장에서는 인덱스를 지원하므로, 모델에 인덱스 설정을 지원하고 마이그레이션을 하면 인덱스를 통해 유사 문서 검색 속도를 향상시킬 수 있습니다.
``sqlite-vec`` 확장에서는 인덱스를 지원하지만, 아직 ``django-pyhub-rag`` 라이브러리에서는 인덱스를 지원하지 않습니다.
``pgvector`` 확장과 동일한 인터페이스로 지원 예정입니다.

만약 2000 차원을 초과한 임베딩이 필요한 경우 ``embedding`` 필드를 재정의하고, ``text-embedding-3-large`` 임베딩 모델을 사용합니다.

.. tab-set::

    .. tab-item:: sqlite

        .. code-block:: python
            :caption: ``chat/models.py``
            :emphasize-lines: 1,5-9

            from pyhub.rag.fields.sqlite import SQLiteVectorField
            from pyhub.rag.models.sqlite import SQLiteVectorDocument

            class TaxLawDocument(SQLiteVectorDocument):
                embedding = SQLiteVectorField(
                    dimensions=3072,
                    editable=False,
                    embedding_model="text-embedding-3-large",
                )

    .. tab-item:: postgres

        .. code-block:: python
            :caption: ``chat/models.py``
            :emphasize-lines: 1,5-9

            from pyhub.rag.fields.postgres import PGVectorField
            from pyhub.rag.models.postgres import PGVectorDocument

            class TaxLawDocument(PGVectorDocument):
                embedding = PGVectorField(
                    dimensions=3072,
                    editable=False,
                    embedding_model="text-embedding-3-large",
                )

준비한 세법 해석례 데이터는 3072 차원 임베딩을 가지고 있으므로, 위 코드처럼 임베딩 필드를 재정의하여 3072 차원 임베딩을 생성합니다.


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
