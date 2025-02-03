=============================================
[docker] Postgres 서버 구동하기
=============================================

`Docker Hub <https://hub.docker.com>`_\에서 Postgres 공식 이미지 `postgres <https://hub.docker.com/_/postgres>`_\를 지원합니다.
`지원 Tags <https://hub.docker.com/_/postgres/tags>`_\를 참고해서 원하는 버전으로 설치하실 수 있습니다.
아래에서는 16 버전으로서 ``postgres:16`` 이미지를 사용하겠습니다.

.. tab-set::

    .. tab-item:: shell

        .. code-block:: shell
            :emphasize-lines: 2,9

            docker run \
                --name pg-db \
                -e POSTGRES_USER=djangouser \
                -e POSTGRES_PASSWORD=djangopw \
                -e POSTGRES_DB=django_db \
                -p 5432:5432 \
                -v pg_data:/var/lib/postgresql/data \
                -d \
                postgres:16

    .. tab-item:: powershell

        .. code-block:: powershell
            :emphasize-lines: 2,9

            docker run `
                --name pg-db `
                -e POSTGRES_USER=djangouser `
                -e POSTGRES_PASSWORD=djangopw `
                -e POSTGRES_DB=django_db `
                -p 5432:5432 `
                -v pg_data:/var/lib/postgresql/data `
                -d `
                postgres:16

    .. tab-item:: Docker Compose

        .. code-block:: yaml
           :caption: docker-compose.yml
           :emphasize-lines: 2,3

            services:
              pg_db:
                image: "postgres:16"
                environment:
                  POSTGRES_USER: djangouser
                  POSTGRES_PASSWORD: djangopw
                  POSTGRES_DB: django_db
                ports:
                  - "5432:5432"
                volumes:
                  - pg_db_data:/var/lib/postgresql/data

            volumes:
              pg_db_data:

        위 서비스 외에 필요한 서비스를 추가하시고, 아래 명령으로 구동하실 수 있습니다.

        .. code-block:: shell

            # docker-compose.yml 내역대로 컨테이너들을 백그라운드에서 실행
            docker-compose up -d

            # 컨테이너 내역 확인
            docker-compose ps

            # 컨테이너 모두 중지
            docker-compose down

.. tip::

    pgvector 확장이 지원되는 이미지는 `pgvector/pgvector:pg16 <https://hub.docker.com/r/pgvector/pgvector/tags>`_\를 사용해주세요.


환경변수
==============

인증 정보로서 아래 3가지 환경변수를 설정했구요.
추가적인 환경변수는 `공식문서의 Environment Variables 섹션 <https://hub.docker.com/_/postgres>`_\을 참고해주세요.

* ``POSTGRES_USER`` : 유저명
* ``POSTGRES_PASSWORD`` : 암호
* ``POSTGRES_DB`` : 데이터베이스 명


디폴트 포트
==============

Postgres 디폴트 포트는 ``5432`` 입니다. 호스트 머신에도 동일한 포트로 노출하기 위해 ``-p 5432:5432`` 옵션을 추가했습니다.
기존에 ``5432`` 포트를 사용하고 있는 서비스가 있으면 컨테이너 구동에 실패합니다.
호스트 포트번호를 ``15432``\로 매핑할려면 ``-p 15432:5432`` 옵션으로 지정해주세요.
그러면 호스트 머신에서 ``15432`` 포트로 접속할 수 있습니다.


도커 볼륨
==============

컨테이너를 제거하더라도 데이터베이스 데이터를 보존하기 위해 ``-v pg_data:/var/lib/postgresql/data`` 볼륨 옵션을 추가했습니다.
이는 Docker 볼륨을 생성하여 컨테이너의 ``/var/lib/postgresql/data`` 디렉터리를 호스트의 ``pg_data`` 볼륨에 마운트하는 것입니다.
Docker 볼륨은 컨테이너와 독립적으로 관리되므로, 컨테이너가 제거되더라도 볼륨은 유지되어 데이터베이스 데이터가 보존됩니다.


백그라운드 실행
===================

데이터베이스를 백그라운드에서 실행되도록 ``-d`` 옵션을 추가했습니다.


로그 확인
================

환경변수 오류 등의 이유로 컨테이너 구동에 실패할 수도 있구요.
서버가 구동되어 데이터베이스 연결 준비가 될 때까지 시간이 다소 걸릴 수 있습니다.
연결 준비가 완료될 때까지는 데이터베이스 연결이 실패합니다.

``docker logs -f 컨테이너명`` 명령으로 컨테이너 로그를 확인하여, 데이터베이스 연결 준비를 확인해주세요.
아래와 같이 ``listening on IPv4 address "0.0.0.0", port 5432`` 로그가 확인되면,
데이터베이스 연결 준비가 완료된 것입니다.

.. admonition:: 로그 예시

    .. code-block:: text
        :emphasize-lines: 1,13

        $ docker logs -f pg-db

        The files belonging to this database system will be owned by user "postgres".
        This user must also own the server process.

        The database cluster will be initialized with locale "en_US.utf8".
        The default database encoding has accordingly been set to "UTF8".
        The default text search configuration will be set to "english".

        생략

        2025-02-03 12:16:00.628 UTC [1] LOG:  starting PostgreSQL 16.0 (Debian 16.0-1.pgdg120+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 12.2.0-14) 12.2.0, 64-bit
        2025-02-03 12:16:00.631 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
        2025-02-03 12:16:00.631 UTC [1] LOG:  listening on IPv6 address "::", port 5432
        2025-02-03 12:16:00.633 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
        2025-02-03 12:16:00.639 UTC [64] LOG:  database system was shut down at 2025-02-03 12:16:00 UTC
        2025-02-03 12:16:00.650 UTC [1] LOG:  database system is ready to accept connections

.. TODO: restart 옵션 검증 후에 내용 추가
.. .. tip::

..     호스트 머신이 재시작되면 이 도커 컨테이너는 자동으로 재시작되지 않고 정지 상태가 됩니다.
..     컨테이너를 자동으로 재시작하려면 ``--restart unless-stopped`` 옵션을 추가해주세요.

..     * ``no`` (기본값) : 컨테이너가 중지된 후 자동으로 다시 재시작되지 않습니다.
..     * ``unless-stopped`` : 수동으로 중지하지 않는 한 자동 재시작됩니다.
..     * ``always`` : 수동으로 중지해도 항상 재시작됩니다.
..     * ``on-failure`` : 컨테이너가 비정상 종료로 인해 중지된 경우에만 재시작됩니다.


연결 문자열
=================

연결 문자열은 아래와 같습니다. 장고 프로젝트에서 ``DATABASE_URL`` 환경변수로 사용해주세요.

.. code-block:: text

    postgresql://djangouser:djangopw@localhost:5432/django_db

호스트 측 포트번호를 ``15432``\로 변경했다면 아래와 같습니다.

.. code-block:: text

    postgresql://djangouser:djangopw@localhost:15432/django_db
