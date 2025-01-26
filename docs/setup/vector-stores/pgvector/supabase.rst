=============================================
[supabase] Postgre pgvector 설정하기
=============================================

시작하시기 전에
===================

:doc:`/setup/databases/postgres/supabase` 문서를 참고해서,
supabase 데이터베이스를 생성하시고 ``DATABASE_URL`` 연결 문자열을 획득해주세요.


pgvector 확장 활성화
========================

.. admonition:: 공식문서
    :class: tip

    `pgvector: Embeddings and vector similarity <https://supabase.com/docs/guides/database/extensions/pgvector?queryGroups=database-method&database-method=dashboard>`_

supabase에는 이미 pgvector 확장이 준비되어 있습니다.
대시보드를 통해 활성화를 시키실 수도 있고, SQL을 통해 활성화를 시키실 수도 있습니다.

좌측 사이드바에서 ``Database`` → ``Extensions`` 탭을 클릭해주세요.
가용한 확장 중에 ``vector`` 확장이 있습니다. 스위치를 클릭해서 디폴트 옵션으로 활성화해주세요.

.. tab-set::

    .. tab-item:: 확장 활성화하기 전

        .. image:: ./assets/supabase-01-pgvector.png

    .. tab-item:: 확장 활성화한 후

        .. image:: ./assets/supabase-02-pgvector.png

    .. tab-item:: SQL을 직접 사용할 경우

        .. code-block:: sql

            -- Example: enable the "vector" extension.
            create extension vector
            with
              schema extensions;

            -- Example: disable the "vector" extension
            drop
              extension if exists vector;
