===============
MySQL, MariaDB
===============

    국내에서 가장 대중적인 관계형 데이터베이스


필수 확장
==================

`django-mysql 라이브러리 <https://django-mysql.readthedocs.io>`_\를 통해, 다양한 MySQL 고급 기능 지원


드라이버
======================

* 선택지 #1 : `pymysql <https://pymysql.readthedocs.io>`_ (순수 파이썬) + `cryptography <https://cryptography.io>`_

  - C 코드없이 파이썬 코드만 있으므로, 설치가 쉽기에 로컬 개발환경에 추천 (특히 윈도우)

* 선택지 #2 : `mysqlclient <https://mysqlclient.readthedocs.io>`_ (C 확장) + `cryptography <https://cryptography.io>`_

  - C 코드로 작성되어 있으므로 성능은 좋지만 빌드 환경 구축이 필요합니다.
    윈도우에서는 구축이 번거롭기에 추천하지 않고, 서버 환경에 추천합니다.


장고 프로젝트에서 pymysql을 사용할 경우
------------------------------------------------

아래 패치를 적용하여, ``pymysql``\을 ``MySQLdb``\로 인식하도록 해주세요.

.. code-block:: python

    import pymysql
    pymysql.install_as_MySQLdb()

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            # ...
        }
    }


장고 프로젝트에서 계정정보가 틀렸을 때
========================================

계정정보가 틀렸거나, 방화벽/네트워크 설정 등의 이슈로 서버에 접속할 수 없을 때에는 아래 오류가 발생합니다.

.. code-block:: text

    django.db.utils.OperationalError: (2003, "Can't connect to MySQL server on 'localhost' ([Errno 61] Connection refused)")


----

.. toctree::
    :maxdepth: 2
    :caption: 문서 목록

    docker
