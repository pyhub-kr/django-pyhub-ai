=============================================
[docker] Postgres 서버 구동하기
=============================================

Docker Hub에서 `postgres 공식 이미지 <https://hub.docker.com/_/postgres>`_\를 지원합니다.
`지원 Tags <https://hub.docker.com/_/postgres/tags>`_\를 참고해서 원하는 버전으로 설치해주세요.
아래에서는 ``16`` 버전을 사용하겠습니다.

인증 정보로서 아래 3가지 환경변수를 설정했구요.
추가적인 환경변수는 `공식문서의 Environment Variables 섹션 <https://hub.docker.com/_/postgres>`_\을 참고해주세요.

* ``POSTGRES_USER`` : 유저명
* ``POSTGRES_PASSWORD`` : 암호
* ``POSTGRES_DB`` : 데이터베이스 명

Postgres는 디폴트 포트 ``5432``\를 사용합니다. 호스트 머신에도 동일한 포트로 노출하기 위해 ``-p 5432:5432`` 옵션을 추가했습니다.
기존에 ``5432`` 포트를 사용하고 있는 서비스가 있으면 컨테이너가 구동되지 않습니다.
``-p 15432:5432`` 옵션과 같이 호스트 측 포트를 변경해주세요.
그러면 호스트 머신에서 ``15432`` 포트로 접속할 수 있습니다.

컨테이너를 제거하더라도 데이터베이스 데이터를 보존하기 위해 ``-v pg_data:/var/lib/postgresql/data`` 볼륨 옵션을 추가했습니다.

데이터베이스를 백그라운드에서 실행되도록 ``-d`` 옵션을 추가했습니다.

.. tab-set::

    .. tab-item:: shell

        .. code-block:: shell

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

연결 문자열은 아래와 같습니다. 장고 프로젝트에서 ``DATABASE_URL`` 환경변수로 사용해주세요.

.. code-block:: text

    postgresql://djangouser:djangopw@localhost:5432/django_db

호스트 측 포트번호를 ``15432``\로 변경했다면 아래와 같습니다.

.. code-block:: text

    postgresql://djangouser:djangopw@localhost:15432/django_db
