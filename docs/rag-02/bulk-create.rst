=====================================================================
개선: make_vector_store 명령에서 다수의 INSERT 쿼리를 묶어서 실행
=====================================================================


.. admonition:: `관련 커밋 <https://github.com/pyhub-kr/django-llm-chat-proj/commit/222c962aa9c6e16d2acb995166fd6c3f9c563345>`_
   :class: dropdown

   * 변경 파일을 한 번에 덮어쓰기 하실려면, :doc:`/utils/pyhub-git-commit-apply` 설치하신 후에, rag-02 폴더 상위 경로에서 아래 명령어 실행

   .. code-block:: bash

      uv run pyhub-git-commit-apply https://github.com/pyhub-kr/django-llm-chat-proj/commit/222c962aa9c6e16d2acb995166fd6c3f9c563345


bulk_create 적용
=====================

아래와 같이 개별 ``INSERT`` 쿼리로 실행하는 것보다

.. code-block:: sql

    INSERT INTO document (page_content, metadata, embedding) VALUES ('...', '...', '...')
    INSERT INTO document (page_content, metadata, embedding) VALUES ('...', '...', '...')
    INSERT INTO document (page_content, metadata, embedding) VALUES ('...', '...', '...')

아래와 같이 묶어서 하나의 ``INSERT`` 쿼리로 실행하면, 데이터베이스와의 통신 횟수를 줄여 훨씬 빠르게 데이터를 저장할 수 있습니다.

.. code-block:: sql

    INSERT INTO document (page_content, metadata, embedding)
           VALUES ('...', '...', '...'), ('...', '...', '...'), ('...', '...', '...')

장고 쿼리셋의 ``bulk_create(batch_size=None)`` 메서드를 활용하면
``batch_size`` 개수만큼 하나의 ``INSERT`` 쿼리로 묶어줍니다.
``batch_size`` 인자를 생략하면 모든 문서를 한 번에 저장합니다.
한 번에 저장하는 개수가 너무 많으면 데이터베이스 메모리 사용량이 과도해져서
데이터베이스에서 오류를 발생할 수 있기에 레코드 개수가 많다면 ``batch_size`` 인자를 꼭 지정해주세요.

아래 코드는 기존의 개별 ``INSERT`` 쿼리로 실행되는 코드이구요.

.. code-block:: python
    :caption: ``chat/management/commands/make_vector_store.py``

    for doc in tqdm(doc_list):
        paikdabang_menu_document = PaikdabangMenuDocument(
            page_content=doc.page_content,
            metadata=doc.metadata,
        )
        paikdabang_menu_document.save()

아래와 같이 모델 인스턴스를 리스트로 모아, 1000개씩 묶어서 데이터베이스로의 저장을 시도해봅니다.

.. code-block:: python
    :caption: ``chat/management/commands/make_vector_store.py``

    # 객체만 생성할 뿐, 아직 데이터베이스 저장 전 입니다.
    paikdabang_menu_documents = [
        PaikdabangMenuDocument(
            page_content=doc.page_content,
            metadata=doc.metadata,
        )
        for doc in doc_list
    ]

    # 1000개씩 묶어서 데이터베이스로의 저장을 시도합니다.
    PaikdabangMenuDocument.objects.bulk_create(paikdabang_menu_documents, batch_size=1000)

실행하면

.. code-block:: bash

    uv run python manage.py make_vector_store ./chat/assets/빽다방.txt

아래와 같이 ``IntegrityError`` 예외가 발생합니다.
``embedding`` 컬럼은 NOT NULL 컬럼인데, 데이터베이스 저장 시에 ``embedding`` 컬럼에 값 지정없이 INSERT 쿼리가 수행되어
NULL 값으로 INSERT 쿼리가 수행되었구요. NOT NULL 제약 조건 위배로 예외가 발생했습니다.
``embedding`` 컬럼에 값이 지정되어 있었다면 예외없이 저장되었을 것입니다.

.. admonition:: 예외 발생: NOT NULL 제약 조건 위배
    :class: warning

    .. figure:: ./assets/bulk-create-integrity-error.png

``PaikdabangMenuDocument`` 모델에서는 ``django-lifecycle`` 훅을 통해 ``save`` 메서드 호출 전에
``embedding`` 필드에 값을 지정하는 데요.
쿼리셋의 ``bulk_create`` 메서드는 각 인스턴스의 ``save()`` 메서드를 호출하지 않기 때문에,
:doc:`django-lifecycle` 페이지에서 지정한 훅이 호출되지 않아 임베딩 값이 생성되지 않은 상황입니다.


bulk_create 시에 임베딩 값을 지원할려면?
==========================================

쿼리셋의 ``bulk_create`` 메서드 호출 시에 임베딩 값이 지정되도록 할려면 어떻게 해야할까요?
``bulk_create`` 메서드를 재정의하여, 부모의 ``bulk_create`` 메서드를 호출하기 전에
``.embedding`` 필드값을 지정하도록 해볼 수 있습니다.
첫번째 인자에는 앞서 생성했던 모델 인스턴스 리스트가 전달됩니다.

.. code-block:: python

    from typing import Iterable

    class PaikdabangMenuDocumentQuerySet(models.QuerySet):
        def bulk_create(self, objs: Iterable["PaikdabangMenuDocument"], *args, **kwargs):
            # 각 모델 인스턴스마다 .embedding 필드에 임베딩 값 할당
            for obj in objs:
                obj.embedding = 계산된 임베딩 값

            # 부모의 bulk_create 메서드 호출하여 데이터베이스에 저장
            return super().bulk_create(objs, *args, **kwargs)

``objs`` 모델 인스턴스 리스트에서 각 모델 인스턴스마다 OpenAI 임베딩 API를 호출하는 것보다,
모아서 API 호출 횟수를 줄이면 네트워크 지연을 훨씬 줄일 수 있습니다.
OpenAI 임베딩 API에서는 여러 문자열의 임베딩을 동시에 요청하는 기능도 제공해줍니다. 😜

* ``str`` 타입의 값일 때에는 인자의 문자열 하나를 임베딩합니다. 각 임베딩 모델의 최대 토큰 수(예: 8191)를 초과해서는 안 됩니다.
* ``List[str]`` 타입의 값으로 지정하여, 한 번의 요청으로 여러 텍스트의 임베딩을 동시에 요청할 수 있습니다.
  리스트 내 각 문자열은 각 임베딩 모델의 최대 토큰 수(예: 8191)를 초과해서는 안 되며,
  리스트 전체는 모델의 요청 제한(Rate Limit)을 초과하지 않는 범위에서 지원됩니다.
  Tier 1 계정일 경우 분당 최대 100만 토큰의 요청을 지원합니다.
  그럼 8090 토큰을 가지는 문자열을 한 번에 최대 124개까지 요청할 수 있습니다.

OpenAI 각 모델의 요청 제한 수는 `공식문서 Rate limits <https://platform.openai.com/docs/guides/rate-limits?tier=tier-one#tier-1-rate-limits>`_\를 통해 확인하실 수 있습니다.
모델 별, `각 계정의 tier <https://platform.openai.com/docs/guides/rate-limits?tier=free#usage-tiers>`_ 별로 제한 수가 다릅니다.

.. list-table:: ``text-embedding-3-small``, ``text-embedding-3-large`` 모델의 요청 제한 수 (2025년 2월 기준)
    :header-rows: 1
    :widths: 11, 20, 22, 20, 27
    :class: align-right

    * - Tier
      - RPM (분당 API 최대 요청수)
      - RPD (하루당 API 최대 요청수)
      - TPM (분당 최대 토큰수)
      - Batch Queue Limit
    * - Free
      - 100
      - 2,000
      - 40,000
      - \-
    * - Tier 1
      - 3,000
      - \-
      - 1,000,000
      - 3백만 :sup:`토큰 (TPM*3배)`
    * - Tier 2
      - 5,000
      - \-
      - 1,000,000
      - 2천만 :sup:`토큰 (TPM*20배)`
    * - Tier 3
      - 5,000
      - \-
      - 5,000,000
      - 1억 :sup:`토큰 (TPM*20배)`
    * - Tier 4
      - 10,000
      - \-
      - 5,000,000
      - 5억 :sup:`토큰 (TPM*100배)`
    * - Tier 5
      - 10,000
      - \-
      - 10,000,000
      - 40억 :sup:`토큰 (TPM*400배)`

.. admonition:: Batch Queue Limit

    Batch Queue Limit는 배치 요청 큐에 대기시킬 수 있는 최대 토큰 수입니다.
    Batch를 활용하면 실시간 임베딩 요청에 비해서 비용이 50% 절감되고, TPM 대비 3배~400배의 토큰 수를 한 번에 대기시킬 수 있습니다.

    Batch에 대기시킬려는 토큰 수가 Batch Queue Limit을 초과한 Batch 요청은 아래 오류가 발생합니다.

        Enqueued token limit reached for text-embedding-3-small in organization org-???.
        **Limit: 20,000,000** enqueued tokens. Please try again once some in_progress batches have been completed.

.. tip::

    OpenAI API 사용량이 많아지면, OpenAI 측에서 Tier를 한 단계씩 올려줍니다.


embed 함수에 리스트 지원 추가하기
==========================================

``PaikdabangMenuDocument`` 모델의 두 ``embed`` 함수에 리스트 지원을 추가합니다.
OpenAI 임베딩 API 응답에서 ``response.data``\는 항상 리스트입니다.

* ``input`` 인자로 문자열을 지정하면, 하나의 임베딩을 수행하고 ``response.data`` 는 벡터값 하나를 가지는 리스트를 반환합니다.
* ``input`` 인자로 문자열 리스트를 지정하면, 여러 임베딩을 수행하고 ``response.data`` 는 다수의 벡터값을 가지는 리스트를 반환합니다.

인자로 문자열을 받으면 벡터값 하나를 반환하고, 문자열 리스트를 받으면 벡터값 리스트를 반환토록 변경하겠습니다.

.. code-block:: python
    :emphasize-lines: 1,7,13-15,18,24-26
    :linenos:

    from typing import List, Union

    class PaikdabangMenuDocument(LifecycleModelMixin, models.Model):
        # ...

        @classmethod
        def embed(cls, input: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
            client = openai.Client(api_key=cls.openai_api_key, base_url=cls.openai_base_url)
            response = client.embeddings.create(
                input=input,
                model=cls.embedding_model,
            )
            if isinstance(input, str):
                return response.data[0].embedding
            return [v.embedding for v in response.data]

        @classmethod
        async def aembed(cls, input: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
            client = openai.AsyncClient(api_key=cls.openai_api_key, base_url=cls.openai_base_url)
            response = await client.embeddings.create(
                input=input,
                model=cls.embedding_model,
            )
            if isinstance(input, str):
                return response.data[0].embedding
            return [v.embedding for v in response.data]


bulk_create 메서드에 적용하기
=====================================

이제 아래와 같이 ``objs`` 리스트에서 문자열 리스트를 생성한 후에, 벡터값을 생성/저장하고,
부모의 ``bulk_create`` 메서드를 호출하여 데이터베이스에 저장할 수 있습니다.

.. code-block:: python
    :linenos:

    from typing import Iterable, List

    class PaikdabangMenuDocumentQuerySet(models.QuerySet):
        def bulk_create(self, objs: Iterable["PaikdabangMenuDocument"], *args, **kwargs):
            # 문자열 리스트 생성    
            input_list: List[str] = [obj.page_content for obj in objs]

            # 문자열 리스트를 벡터 리스트로 **한 번의 API 요청**으로 변환
            embedding_list: List[List[float]] = self.model.embed(input_list)

            # 각 순서대로 개별 인스턴스에 벡터 값 할당
            for obj, embedding in zip(objs, embedding_list):
                obj.embedding = embedding

            # 부모의 bulk_create 메서드 호출하여 데이터베이스에 저장
            return super().bulk_create(objs, *args, **kwargs)

위 코드는 Rate Limit을 초과하지 않는 범위 내에서는 잘 동작합니다.
하나의 문자열에 대한 임베딩 토큰 수가 ``8090`` 일때, 124개 문자열을 임베딩 요청하면 총 토큰 수는 100만이 넘게 됩니다.
Tier 2 계정일 경우 TPM(분당 최대 토큰수)이 100만 이므로, TPM 제한에 걸려 아래와 같은 ``RateLimitError`` 예외가 발생합니다.

.. admonition:: 예외 발생
    :class: warning

    RateLimitError: Error code: 429 - {'error': {'message': 'Request too large for text-embedding-3-small in organization
    org-************************ on tokens per min (TPM): Limit **1000000**, Requested **1003160**.
    The input or output tokens must be reduced in order to run successfully.
    Visit https://platform.openai.com/account/rate-limits to learn more.',
    'type': 'tokens', 'param': None, 'code': 'rate_limit_exceeded'}}


TPM 허용 범위 만큼 묶어서 임베딩 요청하기
==============================================

Tier 1 계정일 경우 ``text-embedding-3-small`` 모델 TPM(분당 최대 토큰수) 제한이 1,000,000 이므로,
계정당 1분에 최대 1,000,000 토큰까지 임베딩할 수 있습니다.
각 계정의 TPM 제한은
`공식문서 <https://platform.openai.com/docs/guides/rate-limits?tier=tier-one#tier-1-rate-limits>`_\를
통해서만 알 수 있을 뿐 API를 통한 조회는 지원하지 않기에,
``RAG_EMBEDDING_MAX_TOKENS_LIMIT`` 설정을 통해 직접 제한 설정을 두고
이 설정 값에 맞춰 그룹을 만들어 그룹 단위로 임베딩 요청하도록 하겠습니다.

.. code-block:: python
    :emphasize-lines: 4-5
    :caption: ``mysite/settings.py``

    OPENAI_API_KEY = env.str("OPENAI_API_KEY", default=None)
    RAG_EMBEDDING_MODEL = env.str("RAG_EMBEDDING_MODEL", default="text-embedding-3-small")
    RAG_EMBEDDING_DIMENSIONS = env.int("RAG_EMBEDDING_DIMENSIONS", default=1536)
    # Tier1, text-embedding-3-small 모델의 TPM : 1,000,000
    RAG_EMBEDDING_MAX_TOKENS_LIMIT = env.int("RAG_EMBEDDING_MAX_TOKENS_LIMIT", default=1_000_000/10)

``PaikdabangMenuDocument`` 모델에도 ``embedding_max_tokens_limit`` 클래스 변수를 추가하고, 디폴트 값으로
``RAG_EMBEDDING_MAX_TOKENS_LIMIT`` 설정을 지정합니다.

.. code-block:: python
    :emphasize-lines: 5
    :caption: ``chat/models.py``
    :linenos:

    class PaikdabangMenuDocument(LifecycleModelMixin, models.Model):
        openai_api_key = settings.OPENAI_API_KEY
        embedding_model = settings.RAG_EMBEDDING_MODEL
        embedding_dimensions = settings.RAG_EMBEDDING_DIMENSIONS
        embedding_max_tokens_limit = settings.RAG_EMBEDDING_MAX_TOKENS_LIMIT
        # ...

임베딩 API에서는 문자열을 토큰으로 먼저 변환한 뒤에 임베딩 벡터로 최종 변환합니다.
``"hello, world"`` 문자열은 12글자이지만, ``text-embedding-3-small`` 모델에서 토큰은 ``[15339, 11, 1917]``\로서 3개가 되고,
임베딩 벡터는 1536차원으로서 ``[-0.01657603681087494, -0.03527357801795006, ...]``\로 생성됩니다.

토큰 수를 기반으로 여러 문자열들을 그룹으로 묶을려면, 각 문자열들을 토큰으로 변환하고 토큰 수를 계산하는 과정이 필요합니다.
OpenAI에서는 토큰 수를 계산해주는 API는 제공하지 않습니다.
OpenAI 공식문서 `How to count tokens with Tiktoken <https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken>`_\에 따르면
``tiktoken`` 라이브러리를 통해 API 호출없이도 토큰을 생성할 수 있다고 합니다.

``PaikdabangMenuDocument`` 모델에 클래스 함수 ``get_token_size`` 메서드를 추가하여,
모델에 지정된 임베딩 모델을 기준으로 주어진 텍스트의 토큰 수를 계산하여 반환토록 하구요.
``PaikdabangMenuDocumentQuerySet``\에서 토큰 수 계산 시에 활용하겠습니다.

.. code-block:: python
    :linenos:
    :emphasize-lines: 1,8-12

    import tiktoken

    class PaikdabangMenuDocument(LifecycleModelMixin, models.Model):
        embedding_model = settings.RAG_EMBEDDING_MODEL

        # ...

        @classmethod
        def get_token_size(cls, text: str) -> int:
            encoding: tiktoken.Encoding = tiktoken.encoding_for_model(cls.embedding_model)
            token: List[int] = encoding.encode(text or "")
            return len(token)

문자열 리스트를 인자로 받으면, 토큰 수에 기반하여 문자열 그룹을 생성해주는 ``make_groups_by_length`` 함수를 ``chat/utils.py`` 파일에 구현합니다.

쿼리셋의 ``bulk_create`` 메서드에서는 ``make_groups_by_length`` 함수를 활용하여 토큰 수 제한에 맞춰 문자열 리스트를 그룹핑하고,
각 그룹 별로 임베딩 API를 호출하여 임베딩 벡터를 생성합니다.
임베딩 API 호출 시에 Rate Limit 예외가 발생하면 60초 쉰 후에 최대 3번까지 재시도합니다.

.. tab-set::

    .. tab-item:: bulk_create 메서드

        .. code-block:: python
            :linenos:

            import logging
            import time

            from chat.utils import make_groups_by_length

            logger = logging.getLogger(__name__)

            class PaikdabangMenuDocumentQuerySet(models.QuerySet):
                # ...

                def bulk_create(self, objs, *args, max_retry=3, interval=60, **kwargs):
                    # 임베딩된 벡터를 저장할 리스트
                    embeddings = []

                    groups = make_groups_by_length(
                        # 임베딩을 할 문자열 리스트
                        text_list=[obj.page_content for obj in objs],
                        # 그룹의 최대 허용 크기 지정
                        group_max_length=self.model.embedding_max_tokens_limit,
                        # 토큰 수 계산 함수
                        length_func=self.model.get_token_size,
                    )

                    # 토큰 수 제한에 맞춰 묶어서 임베딩 요청
                    for group in groups:
                        for retry in range(1, max_retry + 1):
                            try:
                                embeddings.extend(self.model.embed(group))
                                break
                            except openai.RateLimitError as e:
                                if retry == max_retry:
                                    raise e
                                else:
                                    msg = "Rate limit exceeded. Retry after %s seconds... : %s"
                                    logger.warning(msg, interval, e)
                                    time.sleep(interval)

                    for obj, embedding in zip(objs, embeddings):
                        obj.embedding = embedding

                    return super().bulk_create(objs, *args, **kwargs)

                # TODO: 비동기 버전 지원
                async def abulk_create(self, objs, *args, max_retry=3, interval=60, **kwargs):
                    raise NotImplementedError
                    return await super().abulk_create(objs, *args, **kwargs)


    .. tab-item:: 토큰 수에 기반한 문자열 그룹 생성 함수

        문자열 리스트에서 토큰 수를 기반으로 그룹을 만들어주는 함수 ``make_groups_by_length``\를 아래와 같이 구현합니다.

        .. code-block:: python
            :caption: ``chat/utils.py``
            :linenos:

            from logging import getLogger
            from typing import Callable, Generator, Iterable, List

            logger = getLogger(__name__)

            def make_groups_by_length(
                text_list: Iterable[str],
                group_max_length: int,
                length_func: Callable[[str], int] = len,
            ) -> Generator[List[str], None, None]:
                batch, group_length = [], 0
                for text in text_list:
                    text_length = length_func(text)
                    if group_length + text_length >= group_max_length:
                        msg = "Made group : length=%d, item size=%d"
                        logger.debug(msg, group_length, len(batch))
                        yield batch  # 현재 배치 반환
                        batch, group_length = [], 0
                    batch.append(text)
                    group_length += text_length
                if batch:
                    msg = "Made group : length=%d, item size=%d"
                    logger.debug(msg, group_length, len(batch))
                    yield batch  # 마지막 배치 반환

``make_vector_store`` 명령을 수행해보시면, ``빽다방.txt`` 파일에 대해서는 하나의 그룹만 생성이 되었구요.
이는 한 번의 임베딩 API 요청 만으로 임베딩을 수행했음을 의미합니다.

.. code-block:: text
    :emphasize-lines: 1,5

    $ uv run python manage.py make_vector_store ./chat/assets/빽다방.txt
    loaded 1 documents
    split into 10 documents
    100%|████████████████████████████████| 10/10 [00:00<00:00, 12409.18it/s]
    [2025-02-02 10:41:22,525] Made group : length=854, item size=10


embedding 필드가 지정된 인스턴스는 제외하고 임베딩 벡터를 생성하기
============================================================================

``bulk_create`` 메서드 호출 시에 ``.embedding`` 필드가 지정된 인스턴스가 있을 수 있습니다.
다음 페이지에 소개하는 :doc:`batch`\가 적용되면, 별도의 프로세스로 벡터를 생성하고,
``bulk_create`` 메서드 호출 시에 이미 생성된 벡터를 할당하고 데이터베이스에 저장합니다.

아래와 같이 ``bulk_create`` 메서드 호출 시에 ``.embedding`` 필드가 지정되지 않은 인스턴스만 추출하여
해당 인스턴스들에 대해서만 임베딩 벡터를 생성토록 개선합니다.

.. code-block:: python
    :linenos:
    :caption: ``chat/models.py``
    :emphasize-lines: 6-9,16,37

    class PaikdabangMenuDocumentQuerySet(models.QuerySet):
        # ...

        def bulk_create(self, objs, *args, max_retry=3, interval=60, **kwargs):
            # 임베딩 필드가 지정되지 않은 인스턴스만 추출
            non_embedding_objs = [obj for obj in objs if obj.embedding is None]

            # 임베딩되지 않은 인스턴스가 있으면, 해당 인스턴스들에 대해서만 임베딩 벡터 생성
            if len(non_embedding_objs) > 0:

                # 임베딩된 벡터를 저장할 리스트
                embeddings = []

                groups = make_groups_by_length(
                    # 임베딩을 할 문자열 리스트
                    text_list=[obj.page_content for obj in non_embedding_objs],
                    # 그룹의 최대 허용 크기 지정
                    group_max_length=self.model.embedding_max_tokens_limit,
                    # 토큰 수 계산 함수
                    length_func=self.model.get_token_size,
                )

                # 토큰 수 제한에 맞춰 묶어서 임베딩 요청
                for group in groups:
                    for retry in range(1, max_retry + 1):
                        try:
                            embeddings.extend(self.model.embed(group))
                            break
                        except openai.RateLimitError as e:
                            if retry == max_retry:
                                raise e
                            else:
                                msg = "Rate limit exceeded. Retry after %s seconds... : %s"
                                logger.warning(msg, interval, e)
                                time.sleep(interval)

                for obj, embedding in zip(non_embedding_objs, embeddings):
                    obj.embedding = embedding

            return super().bulk_create(objs, *args, **kwargs)
