================================
👨‍💻 핸즈온랩 시간. 실습환경 확인
================================

:doc:`./preparation` 문서에서 확인했었던 실습환경을 재차 확인합니다.

* :ref:`sqlite-vec 라이브러리를 활용하실 경우 <sqlite-vec>`

  - 시스템 확인 코드 동작 확인

* :ref:`pgvector 라이브러리를 활용하실 경우 <pgvector>`

  - supabase.com 서비스에 가입하고, ``DATABASE_URL`` 환경변수 준비


sqlite-vec 라이브러리를 활용하실 경우
==============================================

.. _sqlite-vec:

실습환경 재확인
---------------------

시스템 확인 코드를 통해 실습환경을 확인합니다. 운영체제/쉘에 맞게 명령을 복사해서 실행해주세요.

.. tab-set::

    .. tab-item:: 윈도우 파워쉘/명령프롬프트

        .. code-block:: powershell

            powershell -Command "(iwr https://gist.githubusercontent.com/allieus/aa62bffa2aaf26085eb11b3b4e98d9e6/raw/sqlite3-check-system.py).Content" | python

    .. tab-item:: macOS 쉘

        .. code-block:: shell

            curl https://gist.githubusercontent.com/allieus/aa62bffa2aaf26085eb11b3b4e98d9e6/raw/sqlite3-check-system.py | python


실습환경 준비 완료
---------------------

``This Python supports sqlite3 extension. See you at the venue. ;-)`` 문장이 출력되면 실습환경 준비가 완료된 것입니다.

.. figure:: ./assets/win-check-system.png


pgvector 라이브러리를 활용하실 경우
========================================

.. _pgvector:

https://supabase.com 서비스를 이용하시거나, 로컬에 ``pgvector`` 확장이 설치된 ``PostgreSQL`` 데이터베이스를 생성하신 후에,
``DATABASE_URL`` 환경변수로서 사용할 연결 문자열을 준비해주세요.

.. code-block:: text
    :caption: ``DATABASE_URL`` 환경변수 예시

    postgresql://postgres.euvmdqdkpiseywirljvs:암호@aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres


Let's Go!
==========

잘 부탁드립니다. 😉
