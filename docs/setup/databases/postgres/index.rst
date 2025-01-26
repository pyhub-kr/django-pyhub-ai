========
Postgres
========

    국내외에서 인기가 점점 높아지고 있는 관계형 데이터베이스이며, 뛰어난 확장성이 강점.


장고에서 지원하는 PostgreSQL 만의 고급 기능
==============================================

https://docs.djangoproject.com/en/dev/ref/contrib/postgres/

* PostGIS 확장 (GIS 지원)

* ArrayField (배열 필드)

* HStoreField (Key/Value 필드)

* JSONField (JSONB 타입)

* RangeField (범위)

* SearchVector/SearchQuery (텍스트 검색)


pg-vector 확장
-----------------

* :doc:`/setup/vector-stores/pgvector/index`


드라이버
==============

psycopg2
---------

* Windows : whl 팩키지 설치
* macOS/Linux : 소스코드 다운로드 & 빌드 설치 시도 (관련 라이브러리와 빌드 툴이 없으면 빌드 오류)

psycopg2-binary
---------------

* Windows : whl 팩키지 설치
* macOS/Linux : whl 팩키지 설치 (편리)


settings
========

.. code-block:: python

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            # ...
        }
    }


장고 프로젝트에서 계정정보가 틀렸을 때
========================================

계정정보가 틀렸거나, 방화벽/네트워크 설정 등의 이슈로 서버에 접속할 수 없을 때에는 아래 오류가 발생합니다.

.. code-block:: text

    django.db.utils.OperationalError: connection to server at "localhost" (::1), port 5432 failed: Connection refused
        Is the server running on that host and accepting TCP/IP connections?
    connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused
        Is the server running on that host and accepting TCP/IP connections?


----

.. toctree::
    :maxdepth: 2

    supabase
    docker
