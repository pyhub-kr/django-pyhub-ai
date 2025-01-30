=====================================
[linux] Postgres 서버 설치하기
=====================================

우분투 ``22.10``\에서 테스트되었습니다.


공식 저장소를 통해 설치하기
============================

우분투에서는 공식 저장소에서 Postgres 데이터베이스를 지원합니다.
2025년 1월 기준으로 16 버전이 제공되고 있으며,
보다 최신 버전이 필요하시다면 `Postgres APT 저장소를 추가 <https://wiki.postgresql.org/wiki/Apt>`_\하셔야 합니다.

.. code-block:: shell

    sudo apt update
    sudo apt install -y postgresql-16

    # pgvector 확장이 필요할 경우 추가로 설치합니다.
    # sudo apt install -y postgresql-16-pgvector

``sudo systemctl status postgresql`` 명령을 통해 서버 구동 상황을 확인해주세요.
``Active: active (exited)``\로 표시되면 실행 중 상태입니다.

.. figure:: ./assets/linux-status.png

만약 실행되지 않았다면, 다음 명령으로 실행하고 자동 시작을 활성화할 수 있습니다.

.. code-block:: text

    sudo systemctl start postgresql
    sudo systemctl enable postgresql


데이터베이스 계정 만들기
============================

Postgres 데이터베이스를 설치하면 기본적으로 ``postgres`` 관리 계정이 생성됩니다.
이 계정으로 전환하여 ``psql`` 쉘에 진입할 수 있습니다.

.. code-block:: text

    $ sudo -u postgres psql
    psql (16.6 (Ubuntu 16.6-0ubuntu0.24.10.1))
    Type "help" for help.

    postgres=#

``django_db`` 이름의 데이터베이스를 생성하고,

.. code-block:: text

    postgres=# CREATE DATABASE django_db;
    CREATE DATABASE

``djangouser`` 계정을 생성하며 암호도 같이 지정합니다.

.. code-block:: text

    postgres=# CREATE USER djangouser WITH ENCRYPTED PASSWORD 'djangopw';
    CREATE ROLE

이후 암호를 변경하시려면 다음 명령을 사용하세요.

.. code-block:: text

    postgres=# ALTER USER djangouser with ENCRYPTED PASSWORD 'djangopw';
    ALTER ROLE

``django_db`` 데이터베이스에 대한 모든 권한을 ``djangouser`` 계정에 부여합니다.
혹은 `필요한 권한만 부여 <https://www.postgresql.org/docs/current/ddl-priv.html>`_\하실 수도 있습니다.

.. code-block:: text

    postgres=# GRANT ALL PRIVILEGES ON DATABASE django_db TO djangouser;
    GRANT

``psql`` 쉘을 종료합니다.

.. code-block:: text

    postgres=# \q

방금 생성한 유저로 Postgres 데이터베이스에 접속을 확인해봅니다.
``psql`` 쉘이 뜨면 성공입니다.

.. code-block:: text

    $ psql -U djangouser -d django_db -h 127.0.0.1 -p 5432
    Password for user djangouser: 암호입력

    psql (16.6 (Ubuntu 16.6-0ubuntu0.24.10.1))
    SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
    Type "help" for help.

    django_db=>


외부 접속을 허용할려면
========================

Postgres에서는 보안을 위해 기본적으로 외부 접속을 허용하지 않습니다.
장고 서버가 구동되는 머신에서 데이터베이스를 운영하실 경우 외부 접속을 허용하실 필요는 없습니다.
다만 다른 머신에서 데이터베이스에 접속하실 필요가 있을 경우, 다음 설정을 통해 외부 접속을 허용할 수 있습니다.
먼저 ``/etc/postgresql/16/main/postgresql.conf`` 파일을 열어 외부 접속을 허용해줍니다.)

.. code-block:: text

    listen_addresses = '*'

``*`` 값을 설정하면 모든 아이피에서 접속할 수 있으며, 특정 아이피로부터의 접속만 허용할려면 ``listen_addresses = '192.168.1.100'`` 와 같이 설정하시면 됩니다.

.. tip::

    Postgres 디폴트 포트번호는 5432입니다.
    다른 포트로 변경하실려면 ``/etc/postgresql/16/main/postgresql.conf`` 설정에서 ``port`` 값을 변경하시고,
    Postgres 서버를 재시작하여 설정을 적용해주세요.

이어서 ``/etc/postgresql/16/main/pg_hba.conf`` 파일을 열어, 외부 접속에 대한 인증 방식을 추가해야만 합니다.
디폴트 설정으로 로컬 접속에 대해서만 인증 방식이 지정되어있습니다.

.. code-block:: text

    # Database administrative login by Unix domain socket
    local   all             postgres                                peer

    # TYPE  DATABASE        USER            ADDRESS                 METHOD
    local   all             all                                     peer
    host    all             all             127.0.0.1/32            scram-sha-256
    host    all             all             ::1/128                 scram-sha-256
    local   replication     all                                     peer
    host    replication     all             127.0.0.1/32            scram-sha-256
    host    replication     all             ::1/128                 scram-sha-256

.. tip::

    ``psql`` 접속에서 호스트를 지정하지 않으면(``-h`` 옵션을 생략하면) 로컬 접속이 되며 ``peer`` 인증 방식이 사용됩니다.
    ``peer`` 인증 방식은 운영체제의 계정 정보를 활용하는 방식입니다.
    이는 ``psql`` 쉘에 접속하려면 데이터베이스 사용자와 동일한 이름의 리눅스 계정이 필요합니다.
    예를 들어 ``djangouser`` 계정으로 접속하려면 리눅스에도 동일한 이름의 계정이 있어야 하며,
    그렇지 않으면 ``FATAL: Peer authentication failed for user "djangouser"`` 오류가 발생합니다.

아래 내용을 추가하여 인증 방식을 적용할 아이피 대역을 지정합니다.

.. code-block:: text

    # 모든 아이피에서 접속 허용하기
    host    all             all             0.0.0.0/0               scram-sha-256

    # 192.168.1.0/24 대역에서만 접속 허용하기
    host    all             all             192.168.1.0/24          scram-sha-256

Postgres 서버를 재시작하여 설정을 적용하고, 서버 동작을 확인합니다.
서버 재시작에 실패했다면 변경하신 설정에 오류가 있을 겁니다. 오류를 수정하시고 다시 서버를 재시작해주세요.

.. code-block:: shell

    sudo systemctl restart postgresql
    sudo systemctl status postgresql


연결 문자열
==============

연결 문자열은 아래와 같습니다. 다른 서버에서 접속하실 경우 접속 주소를 변경해주세요.
장고 프로젝트에서 ``DATABASE_URL`` 환경변수로 사용해주세요.

.. code-block:: text

    postgresql://djangouser:djangopw@localhost:5432/django_db
