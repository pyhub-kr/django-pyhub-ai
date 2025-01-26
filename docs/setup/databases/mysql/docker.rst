=============================================
[docker] MySQL 서버 구동하기
=============================================

Docker Hub에서 `MySQL 공식 이미지 <https://hub.docker.com/_/mysql>`_\를 지원합니다.
`지원 Tags <https://hub.docker.com/_/mysql/tags>`_\를 참고해서 원하는 버전으로 설치해주세요.
아래에서는 2025년 1월 기준으로 최신버전 ``9.2``\를 사용합니다.

인증 정보로서 아래 3가지 환경변수를 설정했구요.
추가적인 환경변수는 `공식문서의 Environment Variables 섹션 <https://hub.docker.com/_/mysql>`_\을 참고해주세요.

* ``MYSQL_USER`` : 유저명
* ``MYSQL_PASSWORD`` : 암호
* ``MYSQL_ROOT_PASSWORD`` : 루트 암호
* ``MYSQL_DATABASE`` : 데이터베이스 명

MySQL은 디폴트 포트 ``3306``\를 사용합니다. 호스트 머신에도 동일한 포트로 노출하기 위해 ``-p 3306:3306`` 옵션을 추가했습니다.
기존에 ``3306`` 포트를 사용하고 있는 서비스가 있으면 컨테이너가 구동되지 않습니다.
``-p 13306:3306`` 옵션과 같이 호스트 측 포트를 변경해주세요.
그러면 호스트 머신에서 ``13306`` 포트로 접속할 수 있습니다.

컨테이너를 제거하더라도 데이터베이스 데이터를 보존하기 위해 ``-v mysql_data:/var/lib/mysql`` 볼륨 옵션을 추가했습니다.

데이터베이스를 백그라운드에서 실행되도록 ``-d`` 옵션을 추가했습니다.

.. tab-set::

    .. tab-item:: shell

        .. code-block:: shell

            docker run \
                --name mysql-db \
                -e MYSQL_USER=djangouser \
                -e MYSQL_PASSWORD=djangopw \
                -e MYSQL_ROOT_PASSWORD=djangopw \
                -e MYSQL_DATABASE=django_db \
                -p 3306:3306 \
                -v mysql_data:/var/lib/mysql \
                -d \
                mysql:9.2

    .. tab-item:: powershell

        .. code-block:: powershell

            docker run `
                --name mysql-db `
                -e MYSQL_USER=djangouser `
                -e MYSQL_PASSWORD=djangopw `
                -e MYSQL_ROOT_PASSWORD=djangopw `
                -e MYSQL_DATABASE=django_db `
                -p 3306:3306 `
                -v mysql_data:/var/lib/mysql `
                -d `
                mysql:9.2

    .. tab-item:: Docker Compose

        .. code-block:: yaml
           :caption: docker-compose.yml

            services:
              mysql_db:
                image: "mysql:9.2"
                environment:
                  MYSQL_USER: djangouser
                  MYSQL_PASSWORD: djangopw
                  MYSQL_ROOT_PASSWORD: djangopw
                  MYSQL_DATABASE: django_db
                ports:
                  - "3306:3306"
                volumes:
                  - mysql_db_data:/var/lib/mysql

            volumes:
              mysql_db_data:

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

    mysql://djangouser:djangopw@localhost:3306/django_db

호스트 측 포트번호를 ``13306``\로 변경했다면 아래와 같습니다.

.. code-block:: text

    mysql://djangouser:djangopw@localhost:13306/django_db
