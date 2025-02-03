===========================
pgvector DB 생성
===========================


``pgvector``\가 지원되는 데이터베이스를 생성하고, 장고 프로젝트에 데이터베이스로서 인식시켜보겠습니다.


pgvector 란?
========================

``pgvector`` 확장은 Postgre 데이터베이스 확장으로서 벡터 데이터 타입과 벡터 인덱싱을 지원하여 임베딩 벡터를 효율적으로 저장하고 검색할 수 있습니다.
Postgre 데이터베이스를 그대로 활용할 수 있어 별도의 추가 인프라 없이도 기존 인프라에 빠르게 적용할 수 있습니다.

게다가 파이썬 ``pgvector`` 라이브러리에서는 `장고 통합을 직접 지원 <https://github.com/pgvector/pgvector-python?tab=readme-ov-file#django>`_\하기에 손쉽게 장고 프로젝트에 ``pgvector``\를 통합할 수 있습니다.
`장고는 Postgre 데이터베이스를 통해 가장 많은 기능을 지원 <https://docs.djangoproject.com/en/dev/ref/contrib/postgres/>`_\합니다.


pgvector 데이터베이스 접속 준비
================================

:doc:`/setup/vector-stores/pgvector/index` 문서를 참고해서, 원하시는 방법으로 Postgres 데이터베이스 및 ``pgvector`` 확장을 구성해주세요. 🚀

.. tip::

    개발환경에서는 로컬에 도커를 통한 설치를 권장드리며, 도커 사용이 어려우신 분은 :doc:`supabase 서비스 </setup/vector-stores/pgvector/supabase>` 문서를
    참고해서 ``supabase`` 서비스의 데이터베이스를 활용하시면 간편합니다.

생성하신 데이터베이스에 접속하실 수 있도록 ``DATABASE_URL`` 환경변수를 준비해주시구요.
장고 프로젝트의 ``.env`` 파일에 추가해주세요.
장고 프로젝트에서는 ``django-environ`` 라이브러리를 통해 ``DATABASE_URL`` 환경변수를 파싱하여
``settings.DATABASES["default"]`` 데이터베이스 설정에 반영할 수 있습니다.

.. code-block:: text
    :caption: ``.env`` 파일 예시 (암호는 임의로 가렸습니다.)

    # supabase 서비스를 사용할 때
    DATABASE_URL=postgresql://postgres.euvmdqdkpiseywirljvs:hzD2**********n9@aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres

    # 로컬에 Postgres + pgvector를 설치했을 때 (도커 포함)
    DATABASE_URL=postgresql://djangouser:djangopw@localhost:5432/django_db


장고 프로젝트 데이터베이스 연동 확인
=========================================

장고 프로젝트 디폴트 데이터베이스인 ``SQLite``\는 `파이썬 기본에서 드라이버를 지원 <https://docs.python.org/3/library/sqlite3.html>`_\하기에 별도의 라이브러리 설치없이도 사용할 수 있었습니다.
하지만 :doc:`/setup/databases/postgres/index`\, :doc:`/setup/databases/mysql/index`\, :doc:`/setup/databases/oracle/index` 등의 관계형 데이터베이스를
사용하실려면, 관련 라이브러리를 설치해주셔야 합니다.

:doc:`Postgres 라이브러리 및 설정법 </setup/databases/postgres/index>` 문서를 참고하여
``psycopg2-binary`` 라이브러리를 설치합니다.
윈도우/맥/리눅스 모두에서 라이브러리 빌드없이 ``.whl`` 바이너리 파일로 설치되어 간편합니다.
``psycopg2`` 라이브러리를 설치하시면 윈도우에서는 ``.whl`` 바이너리 파일로 설치되지만,
맥에서는 ``psycopg2`` 버전에 따라 ``.whl`` 바이너리로 설치되지 않고 빌드를 요구하기도 하구요.
리눅스에서는 항상 빌드를 시도하기에 관련 라이브러리와 빌드 툴이 필요해서 조금 번거롭습니다.

.. code-block:: bash

    uv pip install --upgrade psycopg2-binary


``DATABASE_URL`` 환경변수를 적용하기 전에는, 장고 프로젝트는 ``db.sqlite3`` 데이터베이스를 사용했었는 데요.

방금 ``DATABASE_URL`` 환경변수로 새로운 데이터베이스를 지정했고,
``mysite/settings.py`` 내에서 ``env.db()`` 함수를 통해 ``DATABASE_URL`` 환경변수를 파싱하여
``settings.DATABASES["default"]`` 데이터베이스 설정에 반영하고 있습니다.

.. code-block:: python
    :caption: 기존 ``settings.DATABASES`` 설정

    DATABASES = {
        "default": env.db(default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
    }

아래 명령으로 ``settings.DATABASES["default"]`` 데이터베이스 설정 값을 확인해보세요.
``.env`` 파일에 명시한 ``DATABASE_URL`` 환경변수 내역이 반영되어 있음을 확인하실 수 있습니다.
이제 새로운 Postgres 데이터베이스를 바라보고 있습니다.

.. code-block:: text
    :emphasize-lines: 1

    $ uv run python manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default'])"

    {'NAME': 'django_db', 'USER': 'djangouser', 'PASSWORD': 'djangopw', 'HOST': 'localhost', 'PORT': 5432, 'ENGINE': 'django.db.backends.postgresql', 'ATOMIC_REQUESTS': False, 'AUTOCOMMIT': True, 'CONN_MAX_AGE': 0, 'CONN_HEALTH_CHECKS': False, 'OPTIONS': {}, 'TIME_ZONE': None, 'TEST': {'CHARSET': None, 'COLLATION': None, 'MIGRATE': True, 'MIRROR': None, 'NAME': None}}

.. tip::

    지정한 환경변수가 정상적으로 반영이 되었는 지를 어떻게 확인하는 지 방법을 꼭 익히시고, 이를 확인하는 습관은 중요합니다.

    ``.env`` 파일에 명시한 환경변수 값은 설정일 뿐, 이 값이 실제로 반영되었는 지를 확인하는 것은 매우 중요합니다.
    많은 초심자분들이 환경변수 설정을 잘못하거나, 로딩이 누락되거나, 엉뚱한 경로로 로딩하여 데이터베이스 접속에 실패하는 경우가 많습니다.
    이때 ``.env`` 파일만 이래저래 수정하고 있는 경우가 많습니다. 그래서는 문제가 해결되지 않습니다.

    **소스 값이 아닌 실제 반영된 설정을 확인하는 것이 매우 중요합니다.**

``python manage.py showmigrations`` 명령으로 마이그레이션 현황을 확인해보시면,
아래와 같이 모든 마이그레이션이 미적용 상황임을 확인하실 수 있습니다.

.. code-block:: text
    :emphasize-lines: 1

    $ uv run python manage.py showmigrations
    [2025-01-29 07:51:59,219] Loaded vector store 10 items
    accounts
    (no migrations)
    admin
    [ ] 0001_initial
    [ ] 0002_logentry_remove_auto_add
    [ ] 0003_logentry_add_action_flag_choices
    auth
    [ ] 0001_initial
    [ ] 0002_alter_permission_name_max_length
    [ ] 0003_alter_user_email_max_length
    [ ] 0004_alter_user_username_opts
    [ ] 0005_alter_user_last_login_null
    [ ] 0006_require_contenttypes_0002
    [ ] 0007_alter_validators_add_error_messages
    [ ] 0008_alter_user_username_max_length
    [ ] 0009_alter_user_last_name_max_length
    [ ] 0010_alter_group_name_max_length
    [ ] 0011_update_proxy_permissions
    [ ] 0012_alter_user_first_name_max_length
    chat
    (no migrations)
    contenttypes
    [ ] 0001_initial
    [ ] 0002_remove_content_type_name
    sessions
    [ ] 0001_initial

.. warning::

    ``psycopg2-binary`` 혹은 ``psycopg2`` 라이브러리가 사용하시는 가상환경에 설치되어 있지 않다면,
    장고 프로젝트 실행 시 아래와 같은 오류가 발생합니다.

    django.core.exceptions.ImproperlyConfigured: Error loading psycopg2 or psycopg module

아래 명령으로 각 마이그레이션 파일을 모두 적용해주시고, 관리자 계정도 생성해주세요.
로컬 데이터베이스가 아닌 외부 데이터베이스를 사용하므로, ``1234`` 와 같은 암호는
절대 사용하지 마시고 반드시 복잡한 암호로 설정해주세요.

.. code-block:: bash

    uv run python manage.py migrate
    uv run python manage.py createsuperuser
