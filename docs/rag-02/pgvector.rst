===========================
pgvector DB 생성
===========================


``pgvector``\가 지원되는 데이터베이스를 생성하고, 장고 프로젝트에 데이터베이스로서 인식시켜보겠습니다.


pgvector 란?
========================

``pgvector`` 확장은 Postgres 데이터베이스 확장으로서 벡터 데이터 타입과 벡터 인덱싱을 지원하여 임베딩 벡터를 효율적으로 저장하고 검색할 수 있습니다.
Postgres 데이터베이스를 그대로 활용할 수 있어 별도의 추가 인프라 없이도 기존 인프라에 빠르게 적용할 수 있습니다.

게다가 파이썬 ``pgvector`` 라이브러리에서는 `장고 통합을 직접 지원 <https://github.com/pgvector/pgvector-python?tab=readme-ov-file#django>`_\하기에 손쉽게 장고 프로젝트에 ``pgvector``\를 통합할 수 있습니다.
`장고는 Postgres 데이터베이스를 통해 가장 많은 기능을 지원 <https://docs.djangoproject.com/en/dev/ref/contrib/postgres/>`_\합니다.


pgvector 데이터베이스 접속 준비
================================

:doc:`/setup/vector-stores/pgvector/index` 문서를 참고해서, 원하시는 방법으로 Postgres 데이터베이스 및 ``pgvector`` 확장을 구성해주세요. 🚀

* :doc:`supabase 서비스 활용 </setup/vector-stores/pgvector/supabase>` : 간결한 진행을 위해 추천
* :doc:`도커 활용 </setup/vector-stores/pgvector/docker>`
* :doc:`리눅스에서 직접 설치 </setup/vector-stores/pgvector/linux>`

.. tip::

    개발환경에서는 로컬에 도커를 통한 설치를 권장드리며, 도커 사용이 어려우신 분은 :doc:`supabase 서비스 </setup/vector-stores/pgvector/supabase>` 문서를
    참고해서 ``supabase`` 서비스의 데이터베이스를 활용하시면 간편합니다.

위 데이터베이스 가이드에서 ``DATABASE_URL`` 환경변수를 구성하는 방법을 안내드리고 있습니다.
참고하시어 생성하신 데이터베이스에 접속하실 수 있도록 ``DATABASE_URL`` 환경변수를 준비해서,
장고 프로젝트의 ``.env`` 파일에 추가해주세요.

장고 프로젝트에서는 ``django-environ`` 라이브러리를 통해 ``DATABASE_URL`` 환경변수를 파싱하여
``settings.DATABASES["default"]`` 데이터베이스 설정에 반영합니다.
튜토리얼 실습 프로젝트에는 이미 적용되어 있습니다.

.. code-block:: text
    :caption: ``.env`` 파일 예시 (암호는 임의로 가렸습니다.)

    # supabase 서비스를 사용할 때
    DATABASE_URL=postgresql://postgres.euvmdqdkpiseywirljvs:hzD2**********n9@aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres

    # 로컬에 Postgres + pgvector를 설치했을 때 (도커 포함)
    DATABASE_URL=postgresql://djangouser:djangopw@localhost:5432/django_db


장고 프로젝트 데이터베이스 연동 확인
=========================================

장고는 SQLite, Postgres, MySQL, MariaDB, Oracle 관계형 데이터베이스를 공식 지원하며,
``settings.DATABASES`` 설정 변경 만으로 손쉽게 데이터베이스를 교체할 수 있습니다.

.. tip::

    :doc:`/setup/databases/index` 문서에서 장고 프로젝트에서 다양한 데이터베이스를 설정하는 방법을 안내합니다.

장고 프로젝트 디폴트 데이터베이스인 ``SQLite``\는
`파이썬 기본에서 드라이버를 지원 <https://docs.python.org/3/library/sqlite3.html>`_\하기에
별도의 데이터베이스 구축과 라이브러리 설치없이 ``django`` 라이브러리 설치 만으로 즉시 개발을 시작할 수 있었습니다.
하지만 :doc:`/setup/databases/postgres/index`\, :doc:`/setup/databases/mysql/index`\,
:doc:`/setup/databases/oracle/index` 등의 관계형 데이터베이스는 데이터베이스 서버 구축과 그에 따른 드라이버 설치가 필요합니다.

Postgres 드라이버는 2가지 라이브러리로 제공됩니다.

* ``psycopg2`` : 공식 라이브러리이지만, 맥/리눅스에서 버전에 따라 빌드 툴이 필요해서 설치가 조금 번거롭습니다.
* ``psycopg2-binary`` : 윈도우/맥/리눅스 모두에서 라이브러리 빌드없이 ``.whl`` 바이너리 파일로 설치되어 간편합니다.

손쉬운 설치를 위해 ``psycopg2-binary`` 라이브러리를 설치해주세요.

.. code-block:: bash

    uv pip install --upgrade psycopg2-binary


DATABASE_URL 환경변수가 로딩된 상황에서 ``django-environ`` 라이브러리의 ``env.db()`` 함수는
``DATABASE_URL`` 환경변수 값을 파싱하여 ``settings.DATABASES["default"]`` 데이터베이스 설정에 반영합니다.
``DATABASE_URL`` 환경변수가 정의되지 않은 상황에 대응하기 위해 ``default`` 인자를 통해 디폴트 데이터베이스로
SQLite 데이터베이스를 지정했습니다.

.. code-block:: python
    :caption: 기존 ``settings.DATABASES`` 설정
    :emphasize-lines: 2

    DATABASES = {
        "default": env.db(
            default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'
        ),
    }

아래 명령으로 ``settings.DATABASES["default"]`` 데이터베이스 설정 값을 확인해보세요.
``.env`` 파일에 명시한 ``DATABASE_URL`` 환경변수 내역이 반영되어 있음을 확인하실 수 있습니다.
이제 새로운 Postgres 데이터베이스를 바라보고 있고 있습니다. 😉

.. code-block:: text
    :emphasize-lines: 1

    $ uv run python manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default'])"

    {'NAME': 'django_db', 'USER': 'djangouser', 'PASSWORD': 'djangopw', 'HOST': 'localhost', 'PORT': 5432, 'ENGINE': 'django.db.backends.postgresql', 'ATOMIC_REQUESTS': False, 'AUTOCOMMIT': True, 'CONN_MAX_AGE': 0, 'CONN_HEALTH_CHECKS': False, 'OPTIONS': {}, 'TIME_ZONE': None, 'TEST': {'CHARSET': None, 'COLLATION': None, 'MIGRATE': True, 'MIRROR': None, 'NAME': None}}

.. admonition:: 중요
    :class: attention

    ``.env`` 파일에 명시한 환경변수 값은 설정일 뿐, 이 값이 실제로 반영되었는 지를 확인하는 것은 매우 중요합니다.
    많은 초심자분들이 환경변수 설정을 잘못하거나, 로딩이 누락되거나, 엉뚱한 경로로 로딩하여 데이터베이스 접속에 실패하는 경우가 많습니다.
    이때 ``.env`` 파일만 이래저래 수정해보고 "값에는 오류가 없는 데 왜 동작이 안 되지?" 라고 생각을 하시는 거죠.
    그래서는 문제가 해결되지 않습니다.

    실제 적용된 설정값을 확인하시고, 소스값이 제대로 반영되었는 지 확인하는 습관을 기르시는 것이 중요합니다.

``python manage.py showmigrations`` 명령으로 마이그레이션 현황을 확인해보시면,
아래와 같이 모든 마이그레이션이 미적용 상황임을 확인하실 수 있습니다.

.. code-block:: text
    :emphasize-lines: 1

    $ uv run python manage.py showmigrations
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

    .. code-block:: text

        django.core.exceptions.ImproperlyConfigured: Error loading psycopg2 or psycopg module

    사용하시는 가상환경에 ``psycopg2-binary`` 라이브러리를 설치하신 후에 다시 명령을 시도해주세요.
    가상환경에 익숙하지 않으시다면, :doc:`/setup/venv` 문서를 참고하세요.

아래 명령으로 각 마이그레이션 파일을 모두 적용해주시고, 관리자 계정도 생성해주세요.
로컬 데이터베이스가 아닌 외부 데이터베이스를 사용하므로, ``1234`` 와 같은 암호는
절대 사용하지 마시고 반드시 복잡한 암호로 설정해주세요.

.. code-block:: bash

    uv run python manage.py migrate
    uv run python manage.py createsuperuser
