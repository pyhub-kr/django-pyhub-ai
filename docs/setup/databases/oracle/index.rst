======
Oracle
======

    강력한 기능. 좋은 성능. 비싼 라이센스 가격.


드라이버
==============

`oracledb <https://python-oracledb.readthedocs.io>`_ : 오라클 공식 라이브러리로서, 종전 ``cx_Oracle``\가 2022년에 리브랜딩


장고 프로젝트에서 oracledb를 사용할 경우
------------------------------------------------

아래 패치를 적용하여, ``oracledb``\를 ``cx_Oracle``\로 인식하도록 해주세요.

.. code-block:: python

    import sys
    import oracledb as cx_Oracle

    cx_Oracle.version = "8.3.0"  # 2025년 1월 기준 cx_Oracle 최신 버전
    sys.modules["cx_Oracle"] = cx_Oracle


    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.oracle",
            # ...
        }
    }


장고 프로젝트에서 계정정보가 틀렸을 때
========================================

계정정보가 틀렸거나, 방화벽/네트워크 설정 등의 이슈로 서버에 접속할 수 없을 때에는 아래 오류가 발생합니다.

.. code-block:: text

    django.db.utils.OperationalError: DPY-6005: cannot connect to database (CONNECTION_ID=kPwAhDA/iNo3u7lrdaIeRw==).
    [Errno 61] Connection refused
