=============================================
[docker] Postgre pgvector 서버 구동하기
=============================================

직접 Postgres 기반으로 빌드를 하실 수도 있겠지만,
Docker Hub에 `pgvector/pgvector 공식 이미지 <https://hub.docker.com/r/pgvector/pgvector>`_\가 있으니
이를 활용하시면 편리합니다.

:doc:`/setup/databases/postgres/docker` 문서를 참고해서 pgvector 컨테이너를 구동해주세요.
이때 도커 이미지는 ``pgvector/pgvector:pg17``\를 사용해주세요.
``pg17`` 태그 외에도 `다양한 태그 <https://hub.docker.com/r/pgvector/pgvector/tags>`_\가 지원됩니다.
