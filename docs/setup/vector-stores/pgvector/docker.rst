=============================================
[docker] Postgre pgvector 서버 구동하기
=============================================

직접 Postgres 기반으로 빌드를 하실 수도 있겠지만,
Docker Hub에 `pgvector/pgvector 공식 이미지 <https://hub.docker.com/r/pgvector/pgvector>`_\가 있으니
개발환경에서 활용하시면 편리합니다.

:doc:`/setup/databases/postgres/docker` 문서를 참고해서 pgvector 컨테이너를 구동해주세요.
이때 도커 이미지는 ``pgvector/pgvector:pg16``\을 사용해주세요.
``pg16`` 태그 외에도 ``pg17`` 등
`다양한 태그가 지원 <https://hub.docker.com/r/pgvector/pgvector/tags>`_\됩니다.
