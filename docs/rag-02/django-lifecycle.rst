================================================
django-lifecycle hook을 통한 자동 임베딩
================================================


.. admonition:: `관련 커밋 <https://github.com/pyhub-kr/django-llm-chat-proj/commit/28702a8c5f46ba2f336e9db27e32211cf9bac6c8>`_
   :class: dropdown

   * 변경 파일을 한 번에 덮어쓰기 하실려면, :doc:`/utils/pyhub-git-commit-apply` 설치하신 후에, rag-02 폴더 상위 경로에서 아래 명령어 실행

   .. code-block:: bash

      uv run pyhub-git-commit-apply https://github.com/pyhub-kr/django-llm-chat-proj/commit/28702a8c5f46ba2f336e9db27e32211cf9bac6c8


``PaikdabangMenuDocument`` 레코드 생성 시에 ``.page_content`` 필드, ``.metadata`` 필드와 함께
매번 임베딩 값을 계산하고 ``.embedding`` 필드에 저장하는 것은 번거로운 일입니다.

.. code-block:: python
    :emphasize-lines: 4-6,11

    page_content = "hello world"
    metadata = {}

    client = openai.Client()
    res = client.embeddings.create(input=page_content, model="text-embedding-3-small")
    embedding = res.data[0].embedding

    PaikdabangMenuDocument.objects.create(
        page_content=page_content,
        metadata=metadata,
        embedding=embedding,
    )

``PaikdabangMenuDocument`` 모델 내부에서 ``page_content`` 필드 값 생성/변경 시에
``embedding`` 필드 값을 자동으로 생성하도록 하면,

.. code-block:: python

    page_content = "hello world"
    metadata = {}

    PaikdabangMenuDocument.objects.create(
        page_content=page_content,
        metadata=metadata,
    )

다음과 같은 장점이 있습니다:

#. 데이터 일관성 보장: 문서 내용과 임베딩이 항상 동기화되어 있음을 보장할 수 있습니다.
#. 코드 재사용성: 임베딩 생성 로직이 모델에 캡슐화되어 있어 여러 곳에서 일관되게 사용할 수 있습니다.
#. 유지보수성: 임베딩 관련 로직 변경이 필요할 때 한 곳만 수정하면 됩니다.

이를 구현하기 위해 `django-lifecycle <https://rsinger86.github.io/django-lifecycle/>`_ 라이브러리를 활용하겠습니다.
라이브러리를 설치해주세요.

.. code-block:: bash

    uv pip install --upgrade django-lifecycle

장식자를 통해 레코드의 생성/수정/삭제 시점에 특정 메소드를 호출시킬 수 있습니다.
``save`` 메서드를 재정의하거나 ``pre_save`` 시그널을 연결하는 것보다 코드 가독성이 좋고 유지보수가 용이합니다.


임베딩 생성 함수 추가
==============================

먼저 임베딩을 수행할 클래스 함수 ``embed``\를 동기 버전과 비동기 버전으로 구현합니다.
본 페이지에서는 동기 버전만 활용하고, 비동기 버전은 추후 활용하겠습니다.

``update_embedding`` 메서드를 구현하고 ``embed`` 함수를 호출하여 ``page_content`` 필드 값에 대한
벡터값을 계산하고 ``embedding`` 필드에 저장토록 합니다.
이미 임베딩 데이터가 생성되어있는 경우에는 굳이 임베딩 데이터를 생성할 필요가 없으니깐요.
``self.embedding is None`` 조건을 확인하여 임베딩 데이터가 없는 경우에만 임베딩 데이터를 생성합니다.
그리고 ``is_force`` 인자를 받아 강제 업데이트 여부를 결정합니다.
이 함수는 ``embedding`` 필드 만 업데이트할 뿐 데이터베이스 저장을 위한 ``save`` 메서드는 호출하지 않습니다.

.. code-block:: python
    :caption: ``chat/models.py``
    :linenos:
    :emphasize-lines: 1-2,16-19,21-31,33-40

    from typing import List
    import openai

    class PaikdabangMenuDocument(models.Model):
        openai_api_key = settings.RAG_OPENAI_API_KEY
        openai_base_url = settings.RAG_OPENAI_BASE_URL
        embedding_model = settings.RAG_EMBEDDING_MODEL
        embedding_dimensions = settings.RAG_EMBEDDING_DIMENSIONS

        page_content = models.TextField()
        metadata = models.JSONField(default=dict)
        embedding = VectorField(dimensions=embedding_dimensions, editable=False)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        def update_embedding(self, is_force: bool = False) -> None:
            # 강제 업데이트 혹은 임베딩 데이터가 없는 경우에만 임베딩 데이터를 생성합니다.
            if is_force or self.embedding is None:
                self.embedding = self.embed(self.page_content)

        @classmethod
        def embed(cls, input: str) -> List[float]:
            """
            주어진 문자열에 대한 임베딩 벡터를 생성합니다.
            """
            client = openai.Client(api_key=cls.openai_api_key, base_url=cls.openai_base_url)
            response = client.embeddings.create(
                input=input,
                model=cls.embedding_model,
            )
            return response.data[0].embedding

        @classmethod
        async def aembed(cls, input: str) -> List[float]:
            client = openai.AsyncClient(api_key=cls.openai_api_key, base_url=cls.openai_base_url)
            response = await client.embeddings.create(
                input=input,
                model=cls.embedding_model,
            )
            return response.data[0].embedding

        class Meta:
            # 생략

다음 2가지 상황에서는 반드시 ``update_embedding`` 메서드가 호출되어야 합니다.

#. 새로운 ``PaikdabangMenuDocument`` 레코드를 생성할 때
#. 기존 ``PaikdabangMenuDocument`` 레코드에서 ``page_content`` 필드가 변경되었을 때

이 ``update_embedding`` 메서드를 매번 수동으로 호출하는 것은 번거롭고 호출이 누락될 수 있습니다.
``django-lifecycle`` 라이브러리를 통해 생성/수정 시점에 메서드를 자동으로 호출되도록 구성해보겠습니다.


생성/수정 시점에 메서드 자동 호출
====================================================

모델에 ``django-lifecycle`` 라이브러리를 적용할려면, 그 모델은 ``models.Model`` 클래스 대신에 ``LifecycleModel`` 클래스를 상속받아야만 합니다.
``LifecycleModel`` 클래스를 상속받지 않으면 **훅이 호출되지 않습니다**.
부모 모델 클래스 변경이 어려운 경우 ``LifecycleModelMixin`` 클래스를 추가로 상속받아도 됩니다.

.. code-block:: python

    from django_lifecycle import LifecycleModelMixin

    class PaikdabangMenuDocument(LifecycleModelMixin, models.Model):
        ...

모델 클래스에 새로운 메서드를 추가하고, ``@hook(호출시점_지정)`` 장식자를 통해 호출 시점을 지정합니다.
``@hook(BEFORE_CREATE)`` 장식자를 적용하면, 생성 시에 ``save`` 메서드 호출 직전에 자동 호출됩니다.

.. code-block:: python
    :emphasize-lines: 1,6-9

    from django_lifecycle import hook, BEFORE_CREATE, LifecycleModelMixin

    class PaikdabangMenuDocument(LifecycleModelMixin, models.Model):
        ...

        @hook(BEFORE_CREATE)
        def on_before_create(self):
            # 생성 시에 임베딩 데이터가 저장되어있지 않으면 임베딩 데이터를 생성합니다.
            self.update_embedding()

``@hook(BEFORE_UPDATE, when="page_content", has_changed=True)`` 장식자를 적용하면,
수정 시에 ``page_content`` 필드값이 변경되었을 때에만 ``save`` 메서드 호출 직전에 자동 호출됩니다.

.. code-block:: python
    :emphasize-lines: 1,6-9

    from django_lifecycle import hook, BEFORE_CREATE, BEFORE_UPDATE, LifecycleModelMixin

    class PaikdabangMenuDocument(LifecycleModelMixin, models.Model):
        ...

        @hook(BEFORE_UPDATE, when="page_content", has_changed=True)
        def on_before_update(self):
            # page_content 변경 시 임베딩 데이터를 생성합니다.
            self.update_embedding(is_force=True)

코드를 정리하면 아래와 같습니다.

.. code-block:: python
    :caption: ``chat/models.py``
    :linenos:
    :emphasize-lines: 4,19-22,24-27,29-32,34-44,46-56

    from typing import List
    import openai

    from django_lifecycle import hook, BEFORE_CREATE, BEFORE_UPDATE, LifecycleModelMixin

    class PaikdabangMenuDocument(LifecycleModelMixin, models.Model):
        # embedding_model = "text-embedding-3-small"
        openai_api_key = settings.RAG_OPENAI_API_KEY
        openai_base_url = settings.RAG_OPENAI_BASE_URL
        embedding_model = settings.RAG_EMBEDDING_MODEL
        embedding_dimensions = settings.RAG_EMBEDDING_DIMENSIONS

        page_content = models.TextField()
        metadata = models.JSONField(default=dict)
        embedding = VectorField(dimensions=embedding_dimensions, editable=False)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        def update_embedding(self, is_force: bool = False) -> None:
            # 강제 업데이트 혹은 임베딩 데이터가 없는 경우에만 임베딩 데이터를 생성합니다.
            if is_force or self.embedding is None:
                self.embedding = self.embed(self.page_content)

        @hook(BEFORE_CREATE)
        def on_before_create(self):
            # 생성 시에 임베딩 데이터가 저장되어있지 않으면 임베딩 데이터를 생성합니다.
            self.update_embedding()

        @hook(BEFORE_UPDATE, when="page_content", has_changed=True)
        def on_before_update(self):
            # page_content 변경 시 임베딩 데이터를 생성합니다.
            self.update_embedding(is_force=True)

        @classmethod
        def embed(cls, input: str) -> List[float]:
            """
            주어진 문자열에 대한 임베딩 벡터를 생성합니다.
            """
            client = openai.Client(api_key=cls.openai_api_key, base_url=cls.openai_base_url)
            response = client.embeddings.create(
                input=input,
                model=cls.embedding_model,
            )
            return response.data[0].embedding

        @classmethod
        async def aembed(cls, input: str) -> List[float]:
            """
            embed 함수의 비동기 버전
            """
            client = openai.AsyncClient(api_key=cls.openai_api_key, base_url=cls.openai_base_url)
            response = await client.embeddings.create(
                input=input,
                model=cls.embedding_model,
            )
            return response.data[0].embedding

        class Meta:
            indexes = [
                HnswIndex(
                    name="paikdabang_menu_doc_idx",
                    fields=["embedding"],
                    m=16,
                    ef_construction=64,
                    opclasses=["vector_cosine_ops"],
                ),
            ]

이제 ``PaikdabangMenuDocument`` 모델은 ``page_content`` 필드와 ``metadata`` 필드만 채워주고,
``save`` 메서드를 호출하면 자동으로 임베딩 데이터가 생성되고 데이터베이스에 저장됩니다.

.. tip::

    ``django-lifecycle`` 라이브러리의 각 훅은 ``save`` 메서드와 ``delete`` 메서드를 재정의해서 구현되었습니다.
    그래서 ``save`` 메서드나 ``delete`` 메서드가 호출되지 않는 경우에는 훅이 호출되지 않습니다.

    * 쿼리셋의 ``.bulk_create`` 메서드는 ``save`` 메서드를 호출하지 않습니다.
    * 쿼리셋의 ``.bulk_update`` 메서드는 ``save`` 메서드를 호출하지 않습니다.
    * 쿼리셋의 ``.update`` 메서드는 ``save`` 메서드를 호출하지 않습니다.


자동 임베딩 동작 테스트
===========================

``PaikdabangMenuDocument`` 레코드를 생성할 때 ``.page_content`` 필드와 ``.metadata`` 필드만 채워주고 저장합니다.
그럼 인스턴스의 ``save`` 메서드 호출 직전에 ``BEFORE_CREATE`` 훅이 자동 호출되어 임베딩 데이터가 자동으로 채워지고
데이터베이스에 저장됩니다.

.. code-block:: python

    >>> doc = PaikdabangMenuDocument(
    ...     page_content="hello world",
    ...     metadata={},
    ... )
    >>> doc.save()

    >>> print(len(doc.embedding), "차원", doc.embedding[:2], "...")
    1536 차원 [-0.00676333112642169, -0.03919631987810135] ...
