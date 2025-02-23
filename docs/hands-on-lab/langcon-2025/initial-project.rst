=============================================================
장고 프로젝트 생성 및 환경변수 ``OPENAI_API_KEY`` 설정
=============================================================


1. 프로젝트 디렉토리 생성
==========================

원하시는 경로에 ``langcon2025-django-rag`` 프로젝트 폴더를 생성해주세요.


2. 가상환경 생성/활성화
============================

방금 생성하신 프로젝트 폴더로 이동하여 가상환경을 생성/활성화해주세요.

.. tab-set::

    .. tab-item:: 파워쉘/명령프롬프트

        .. code-block:: shell

            python -m venv venv
            venv\Scripts\activate

    .. tab-item:: macOS 쉘

        .. code-block:: shell

            python -m venv venv
            source ./venv/bin/activate

프로젝트 폴더를 편하신 에디터/IDE로 열어주시고, 에디터/IDE에 가상환경도 지정해주세요.


3. .env 파일 생성
====================

프로젝트 루트에 다음 내용으로 ``.env`` 파일을 생성해주세요.

* ``DATABASE_URL`` : 데이터베이스 연결 정보
* ``OPENAI_API_KEY`` : OpenAI API 키

.. note::

    각자 환경에 맞게 ``DATABASE_URL`` 환경변수를 설정해주세요.
    ``OPENAI_API_KEY`` 환경변수는 본인의 OpenAI API 키를 입력해주세요.
    OpenAI API Key는 https://platform.openai.com/api-keys 페이지에서 발급받으실 수 있습니다.

    본인의 OpenAI API Key 생성이 어려우신 분은 핸즈온랩 시간 동안에만 사용하실 Key를 제공해드립니다.

.. tab-set::

    .. tab-item:: sqlite-vec 일 경우

        ``sqlite`` 에서는 ``DATABASE_URL`` 환경변수는 지정하지 않고, 장고 프로젝트 내에서 디폴트 경로를 생성해서 활용하겠습니다.

        .. code-block:: text

            OPENAI_API_KEY=sk-...

    .. tab-item:: pgvector 일 경우

        .. code-block:: text

            DATABASE_URL=postgresql://postgres.euvmdqdkpiseywirljvs:암호@aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres
            OPENAI_API_KEY=sk-...

.. warning::

    ``.env`` 파일은 ``key=value`` 형식으로 작성하시되, 등호 양쪽에 공백이 있으면 안됩니다.
    공백이 있으면 해당 설정은 무시됩니다.


4. 라이브러리 설치
=======================

``sqlite-vec`` 확장을 사용하실 경우, 아래 라이브러리를 설치해주세요.

.. code-block:: shell

    python -m pip install django-pyhub-rag sqlite-vec numpy django-environ django-lifecycle openai

``pgvector`` 확장을 사용하실 경우, 아래 라이브러리를 설치해주세요.

.. code-block:: shell

    python -m pip install django-pyhub-rag psycopg2-binary pgvector django-environ django-lifecycle openai

.. note::

    ``.env`` 파일 로딩을 위해 ``django-environ`` 라이브러리를 설치해주세요.


5. 프로젝트 생성
=======================

.. code-block:: shell

    python -m django startproject mysite .

.. note::

    명령 끝에 ``.``\까지 꼭 포함해주세요. 현재 디렉토리를 기준으로 프로젝트를 생성됩니다.


6. mysite/settings.py 파일 수정
====================================

``.env`` 파일 로딩을 위해 ``django-environ`` 라이브러리를 사용합니다.
프로젝트 루트에 ``.env`` 파일이 있다면 환경변수로서 로딩합니다.

.. code-block:: python
    :caption: ``mysite/settings.py``
    :emphasize-lines: 2,6-9
    :linenos:

    from pathlib import Path
    from environ import Env

    BASE_DIR = Path(__file__).resolve().parent.parent

    env = Env()
    ENV_PATH = BASE_DIR / ".env"
    if ENV_PATH.is_file():
        env.read_env(ENV_PATH, overwrite=True)
    
    # ...

``pyhub.rag`` 앱을 활성화해주세요.

.. code-block:: python
    :caption: ``mysite/settings.py``

    INSTALLED_APPS = [
        # ...
        'pyhub.rag',
    ]

``DATABASE_URL`` 환경변수 값을 읽어 ``default`` 데이터베이스 연결 정보를 설정합니다.
``DATABASE_URL`` 환경변수가 없다면 프로젝트 루트의 ``db.sqlite3`` 경로를 사용합니다.

``sqlite-vec`` 확장은 가상 테이블 (``CREATE VIRTUAL TABLE ...``) 방식으로만 동작합니다. 장고 마이그레이션 시에 가상 테이블로 생성하기 위해
``pyhub.db.backends.sqlite3`` 엔진을 사용합니다.

.. code-block:: python
    :caption: ``mysite/settings.py``

    DATABASES = {
        "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
    }
    if DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3":
        DATABASES["default"]["ENGINE"] = "pyhub.db.backends.sqlite3"

``pyhub.rag`` 앱의 로깅 설정을 추가하여, 디버그 모드에서만 로깅을 출력합니다.

.. code-block:: python
    :caption: ``mysite/settings.py``

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "require_debug_true": {
                "()": "django.utils.log.RequireDebugTrue",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "filters": ["require_debug_true"],
            },
        },
        "loggers": {
            "pyhub": {
                "handlers": ["console"],
                "level": "DEBUG",
            },
        },
    }

``OPENAI_API_KEY`` 환경변수 값을 읽어 ``OPENAI_API_KEY`` 설정을 추가합니다.

.. code-block:: python
    :caption: ``mysite/settings.py``

    # LLM 모델 설정
    OPENAI_API_KEY = env.str("OPENAI_API_KEY")

.. tip::

    환경변수 파싱은 ``settings.py`` 내에서만 수행하고, 장고 프로젝트 내에서는 환경변수 참조없이 ``settings`` 값 참조를 추천드립니다.

다음 명령으로 환경변수 값이 ``settings``\에 정확히 반영되었는 지 확인합니다.

.. code-block:: shell

    python manage.py shell -c "from django.conf import settings; print(settings.DATABASES); print(settings.OPENAI_API_KEY)"

.. tab-set::

    .. tab-item:: sqlite

        ``sqlite``\의 경우 ``ENGINE`` 설정이 반드시 ``pyhub.db.backends.sqlite3`` 엔진으로 설정되어야 합니다.

        .. figure:: ./assets/initial-project-print-settings-sqlite.png

        ``showmigrations`` 명령을 수행해보시면 ``sqlite-vec extension loaded`` 메시지를 확인할 수 있습니다.
        이 메시지가 출력되지 않는다면 다음 2가지를 확인해주세요.

        #. ``settings.DATABASES`` 설정에 ``ENGINE`` 설정이 ``pyhub.db.backends.sqlite3`` 엔진으로 설정되어 있는지 확인
        #. ``settings.INSTALLED_APPS`` 설정에 ``pyhub.rag`` 앱이 포함되어 있는지 확인

        .. figure:: ./assets/initial-project-showmigrations-empty-sqlite.png

    .. tab-item:: postgres

        ``postgres``\의 경우 ``HOST``, ``PORT``, ``USER``, ``PASSWORD``, ``NAME`` 설정을 꼭 확인해주세요.

        .. figure:: ./assets/initial-project-print-settings-postgres.png

        .. figure:: ./assets/initial-project-showmigrations-empty-postgres.png


7. 기본 테이블 생성
=======================

현재 프로젝트에 등록된 장고 앱에 대한 마이그레이션을 수행하여, 데이터베이스 테이블을 생성해주세요.

.. code-block:: shell

    python manage.py migrate
