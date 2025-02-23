========================================
장고 문서 모델 생성 및 마이그레이션
========================================

장고 앱 생성 및 등록
=======================

``chat`` 앱을 생성합니다.

.. code-block:: shell

    python manage.py startapp chat

``chat/urls.py`` 파일을 아래 내용으로 생성합니다.

.. code-block:: python
    :caption: ``chat/urls.py``

    from django.urls import path
    from . import views

    urlpatterns = [
    ]

``mysite/urls.py`` 파일에 ``chat/urls.py`` 패턴을 포함시키고,
루트 URL 요청은 ``chat/`` 주소로 이동시키겠습니다.

.. code-block:: python
    :caption: ``mysite/urls.py``

    from django.contrib import admin
    from django.urls import path, include
    from django.views.generic import RedirectView

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('chat/', include('chat.urls')),
        path('', RedirectView.as_view(url='/chat/')),
    ]

``chat`` 앱을 등록합니다.

.. code-block:: python
    :caption: ``mysite/settings.py``

    INSTALLED_APPS = [
        # ...
        'chat',
    ]


세법 해석례 문서 모델 생성
===============================

``SQLiteDocument`` 추상화 모델과 ``PostgresDocument`` 추상화 모델은

* 디폴트로 1536 차원 ``embedding`` 필드를 가지며 ``text-embedding-3-small`` 임베딩 모델을 사용합니다.
* 2000 차원 초과한 임베딩이 필요한 경우 ``embedding`` 필드를 재정의하고, ``text-embedding-3-large`` 임베딩 모델을 사용합니다.

.. tab-set::

    .. tab-item:: sqlite

        .. code-block:: python
            :caption: ``chat/models.py``

            # from pyhub.rag.fields.sqlite import SQLiteVectorField
            from pyhub.rag.models.sqlite import SQLiteDocument

            class TaxLawDocument(SQLiteDocument):
                # 디폴트로 사용하는 임베딩 모델은 text-embedding-3-small 임베딩 모델을 사용하며,
                # 1536 차원 임베딩을 생성합니다.
                pass

                # 2000 차원 초과한 임베딩이 필요한 경우
                embedding = SQLiteVectorField(
                    dimensions=3072,
                    editable=False,
                    embedding_model="text-embedding-3-large",
                )

    .. tab-item:: postgres

        .. code-block:: python
            :caption: ``chat/models.py``

            # from pyhub.rag.fields.postgres import PostgresVectorField
            from pyhub.rag.models.postgres import PostgresDocument

            class TaxLawDocument(PostgresDocument):
                # 디폴트로 사용하는 임베딩 모델은 text-embedding-3-small 임베딩 모델을 사용하며,
                # 1536 차원 임베딩을 생성합니다.
                pass

                # 2000 차원 초과한 임베딩이 필요한 경우
                embedding = PGVectorField(
                    dimensions=3072,
                    editable=False,
                    embedding_model="text-embedding-3-large",
                )


마이그레이션
===============================

.. tab-set::

    .. tab-item:: sqlite

        .. figure:: ./assets/app-models-0001-makemigrations-sqlite.png

        .. figure:: ./assets/app-models-0001-migrate-sqlite.png

    .. tab-item:: postgres

        .. figure:: ./assets/app-models-0001-makemigrations-postgres.png
