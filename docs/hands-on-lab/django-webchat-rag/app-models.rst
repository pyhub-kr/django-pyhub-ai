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


RAG를 위한 문서 데이터베이스로서의 SQLite
===================================================

SQLite는 단순히 테스트 데이터베이스용 데이터베이스에 그치지 않습니다.

.. admonition:: SQLite의 알려지지 않은 이야기
    :class: dropdown

    * `SQLite의 알려지지 않은 이야기 <https://news.hada.io/topic?id=4558>`_

      - 미국 해군 구축함에 들어가는, 전투 중 피해는 입어도 튼튼하게 동작하는 데이터베이스로서 개발

    * `SQLite를 Primary DB로 사용해보신 분? <https://news.hada.io/topic?id=6498>`_

      - SQLite는 로컬 캐시 목적으로는 정말 끝내주게 편하더군요.
      - SQLite가 정말 좋고 편하긴 합니다만, 작은 웹사이트나 히트가 많지 않은 SaaS에서나 가능하고, 자신의 상황에 대한 판단없이 무턱대고 선택하는 건 위험합니다.

    * `GN⁺: 웹 서버 정적 콘텐츠 저장소로 SQLite 사용 <https://news.hada.io/topic?id=17472>`_

    * `GN⁺: 분산형 SQLite: 패러다임의 전환인가 과장된 선전인가? <https://news.hada.io/topic?id=14445>`_

      - SQLite는 매우 빠름. 싱글 ~40€/m 일반 서버에서 동시에 ~168,000 읽기와 ~8000 쓰기를 지속할 수 있음
      - 하나 이상의 머신이 필요한 상황에서의 SQLite 활용? 주말 프로젝트가 폭발적인 인기를 얻어 빠르게 확장해야 할 수도 있음
      - SQLite는 단순한 백엔드 데이터베이스가 아니라 에지 데이터베이스로 홍보되고 있음
      - SQLite는 정말 놀라운 데이터베이스이지만 대부분의 팀은 SQLite를 피하고 대신 PostgreSQL을 선택하는 것이 좋음
      - 저자의 주장대로 대부분의 백엔드 애플리케이션에서 SQLite를 사용하는 것은 복잡성만 증가시킬 뿐 실질적인 이점이 없어 보임. 이미 검증되고 성숙한 PostgreSQL과 같은 데이터베이스를 사용하는 것이 더 나은 선택일 것임.

    * `GN⁺: 당신이 아마도 SQLite를 사용해야 하는 이유 <https://news.hada.io/topic?id=11561>`_

      - SQLite는 SQL 기반 데이터베이스로 전체 데이터베이스를 단일 파일에 저장하여 간단하고 고급 사용 사례 모두에 간단한 솔루션 제공
      - SQLite는 단일 파일 구조로 인한 제로 지연 시간 제공, "n+1 문제" 감소 및 데이터베이스에 대한 쿼리 수 감소에 대한 개발자의 걱정 감소
      - SQLite는 단순히 파일이며 동일한 앱의 여러 인스턴스를 문제 없이 실행할 수 있으므로 개발 및 테스트 과정을 단순화
      - SQLite는 실시간 사용 사례에 대한 구독 지원 불가, 외부 클라이언트로부터의 연결 허용 불가, Postgres용 TimescaleDB와 같은 플러그인 지원 불가, 열거형 지원 불가 등 일부 제한 사항 존재
      - 이러한 제한 사항에도 불구하고, 저자는 성능, 단순화, 비용 이점으로 인해 SQLite가 대다수의 웹 개발자에게 적합한 솔루션이라고 주장

    * `(Rails World 2024) 오프닝 키노트 - 레일즈 창시자 David Heinemeier Hansson <https://www.youtube.com/watch?v=-cEn_83zRFw>`_

      - `>50x compute, 100x memory, +2TB NVMe <https://youtu.be/-cEn_83zRFw?t=1677>`_ : 하드웨어는 충분히 빨라졌고 (20년 전에 비해 동일가격, x100+), 1대의 물리머신으로도 왠만큼의 서비스를 해낼 수 있으며, SQLite를 사용함으로서 관리 비용을 줄일 수 있다.
      - `DB, 캐시, 큐, 케이블 <https://youtu.be/-cEn_83zRFw>`_

    - `(Rails World 2024) Stephen Margheim - SQLite on Rails: Supercharging the One-Person Framework <https://youtu.be/wFUy120Fts8?t=926>`_

웹서비스에서의 메인 데이터베이스가 아니더라도,
작은 애플리케이션의 메인 데이터베이스로 활용할 수도 있고,
**RAG용 문서를 저장하기 위한 보조 DB로의 활용은 어떠신가요**?

* 장고는 Router 기능을 통해 모델 별로 데이터베이스 호스트/엔진을 쿼리 타임에 동적으로 선택할 수 있습니다.
* SQLite는 파일 기반 데이터베이스이므로, 문서 테이블 파일을 다른 머신으로 복사하고 **읽기전용** 데이터베이스로서 경로만 맞춰주면 OK.

  - 법례와 같은 데이터들이 **자주 변경되지 않는 데이터**\들에 특히 효과적
  - 문서/임베딩이 업데이트되면, 다시 업데이트된 DB 파일만 복사하면 OK.
  - 트래픽이 중앙에 집중되지 않고, 분산되는 효과.


.. admonition:: 참고: `장고 5.1 이상에서 SQLite 최적화 설정 <https://gcollazo.com/optimal-sqlite-settings-for-django/>`_
    :class: dropdown

    SQLite는 기본적으로 데이터베이스 파일에 대한 쓰기 작업 시 전체 데이터베이스에 락(lock)을 걸기 때문에, 동시성이 필요한 웹 애플리케이션에서는 성능 병목이 발생할 수 있습니다. 이러한 문제를 해결하기 위해 WAL(Write-Ahead Logging) 모드를 사용하는 것이 중요합니다.

    WAL 모드는 데이터베이스 변경사항을 별도의 로그 파일에 먼저 기록한 후 나중에 메인 데이터베이스 파일에 적용하는 방식으로, 읽기 작업과 쓰기 작업이 서로 차단되지 않도록 합니다. 이를 통해 동시성이 크게 향상되며, 특히 읽기 작업이 많은 RAG 시스템에서 효과적입니다.

    아래 설정에서 ``PRAGMA journal_mode = WAL;`` 부분이 바로 이 WAL 모드를 활성화하는 설정입니다. 이 설정이 없으면 여러 사용자가 동시에 접근할 때 "database is locked" 오류가 발생할 가능성이 높아집니다.

    또한 ``PRAGMA synchronous = NORMAL;`` 설정은 데이터 안전성과 성능 사이의 균형을 맞추는 설정으로, 트랜잭션 커밋 시 디스크 동기화 빈도를 조절합니다. 기본값인 ``FULL``보다 성능이 향상되면서도 적절한 안전성을 유지합니다.

    아래는 장고 5.1부터 지원하는 ``init_command`` 옵션을 사용한 것이며, 5.1 미만에서도 다른 방법으로 적용 가능합니다.

    .. code-block:: python
        :caption: ``mysite/settings.py``
        :linenos:
        :emphasize-lines: 10-26

        # Database
        # https://docs.djangoproject.com/en/5.1/ref/settings/#databases

        DATABASES = {
            "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        }
        # 모든 SQLite 데이터베이스에 대해 엔진 변경 및 최적화 옵션 적용
        for db_name in DATABASES:
            if DATABASES[db_name]["ENGINE"] == "django.db.backends.sqlite3":
                DATABASES[db_name]["ENGINE"] = "pyhub.db.backends.sqlite3"

                DATABASES[db_name].setdefault("OPTIONS", {})

                # https://gcollazo.com/optimal-sqlite-settings-for-django/
                DATABASES[db_name]["OPTIONS"].update({
                    "init_command": (
                        "PRAGMA foreign_keys=ON;"
                        "PRAGMA journal_mode = WAL;"
                        "PRAGMA synchronous = NORMAL;"
                        "PRAGMA busy_timeout = 5000;"
                        "PRAGMA temp_store = MEMORY;"
                        "PRAGMA mmap_size = 134217728;"
                        "PRAGMA journal_size_limit = 67108864;"
                        "PRAGMA cache_size = 2000;"
                    ),
                    "transaction_mode": "IMMEDIATE",
                    # "transaction_mode": "EXCLUSIVE",
                })


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
