========================================================================
[linux] Postgres 데이터베이스 및 pgvector 확장 설치하기
========================================================================


공식 저장소를 통해 설치하기
===============================

:doc:`/setup/databases/postgres/linux` 문서를 참고하여 리눅스 운영체제에 Postgres 데이터베이스를 설치합니다.

이때 아래 명령으로 ``pgvector`` 확장을 추가로 설치해주세요.

.. code-block:: shell

    sudo apt install -y postgresql-16-pgvector

생성하신 데이터베이스 계정으로 데이터베이스에 접속하신 후에 아래 명령으로 ``pgvector`` 확장을 활성화해주세요.

.. code-block:: sql

    CREATE EXTENSION vector;
