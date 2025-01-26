======
SQLite
======

* 운영이 간단. 서버가 필요없음. 서버 프로세스에 링크되는 그냥 라이브러리.
* 파이썬 기본에서 지원하기에, 추가로 필요한 라이브러리가 없습니다.
* 데이터가 단일 파일에 저장되므로 백업과 이전이 간편 (그냥 복사)
* 동시성이 부족하지만, 완화를 위한 옵션 지원 : WAL (Write-Ahead Logging), 읽기 전용 연결 등
* Litestream, LiteFS : 데이터베이스 실시간 복제 및 외부 스토리지로의 지속적인 백업 지원


SQLite 확장
============

:doc:`/setup/vector-stores/sqlite-vec`\와 같은 SQLite 확장을 사용할려면,
파이썬/장고 프로젝트에서 사용할려면 파이썬에서도 SQLite 확장 지원이 필요합니다.
윈도우 배포판에서는 SQLite 확장이 지원되며, 맥/리눅스에서는 파이썬을 직접 빌드했을 경우 SQLite 확장 지원이 누락되었을 수 있습니다.

SQLite 확장 지원 여부 확인 및 파이썬 재설치에 대해서는 :doc:`/setup/python/index` 문서를 참고해주세요.


장고 settings 설정
=====================

``ENGINE`` 설정으로 ``"django.db.backends.sqlite3"``\를 지정하고, ``NAME`` 설정으로 데이터베이스 파일 경로를 지정합니다.
데이터베이스 파일 경로에 지정한 파일이 없으면, 오류없이 빈 파일이 생성되고, 새로운 데이터베이스 경로로 사용합니다.
새로운 경로의 데이터베이스에서 테이블이 없으므로 데이터베이스에 접근할 경우 ``OperationalError`` 오류가 발생할 수 있습니다.

.. code-block:: python

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

.. warning::

    데이터베이스 파일 경로 지정이 잘못되어 엉뚱한 경로로 데이터베이스를 지정하여,
    기존의 데이터베이스를 참조하지 못하는 경우가 종종 발생합니다.
    특히 ``settings`` 파일을 여러 깊이로 조정할 때
    ``BASE_DIR`` 경로 계산 부분을 조정해줘야하는 데 이 부분이 누락되어 실수가 자주 발생합니다.
    
.. code-block:: python

    env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")


WAL 설정
============

SQLite 데이터베이스에서 쓰기 작업이 발생할 때 전체 데이터베이스가 잠기게 됩니다.
이는 동시성이 필요한 웹 애플리케이션에서 성능 병목이 될 수 있습니다.
WAL(Write-Ahead Logging) 모드는 이러한 문제를 완화하여 데이터베이스 쓰기 성능을 향상시킬 수 있습니다.

* 설정법

  - https://gcollazo.com/optimal-sqlite-settings-for-django/
  - https://blog.pecar.me/sqlite-django-config


추천 영상
--------------

.. raw:: html

    <div class="video-container">
        <iframe
            src="https://www.youtube.com/embed/wFUy120Fts8"
            frameborder="0"
            allowfullscreen>
        </iframe>
    </div>
