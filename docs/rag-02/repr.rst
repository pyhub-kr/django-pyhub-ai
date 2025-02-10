========================================
개선: 쿼리셋 문자열 표현 스타일 다듬기
========================================


.. admonition:: `관련 커밋 <https://github.com/pyhub-kr/django-llm-chat-proj/commit/c5a0135625c115b373b7113ee9e5062c1466b891>`_
   :class: dropdown

   * 변경 파일을 한 번에 덮어쓰기 하실려면, :doc:`/utils/pyhub-git-commit-apply` 설치하신 후에, rag-02 폴더 상위 경로에서 아래 명령어 실행

   .. code-block:: bash

      uv run pyhub-git-commit-apply https://github.com/pyhub-kr/django-llm-chat-proj/commit/c5a0135625c115b373b7113ee9e5062c1466b891


개선 포인트
===============

랭체인의 ``Document`` 인스턴스 리스트를 문자열 표현으로 출력하면

.. code-block:: python

    >>> from langchain_core.documents import Document

    >>> doc_list = [
    ...     Document(metadata={}, page_content='d1'),
    ...     Document(metadata={}, page_content='d2'),
    ... ]

아래와 같이 문자열 표현 안에 ``metadata`` 속성값과 ``page_content`` 속성값이 모두 표현됩니다.

.. code-block:: python

    >>> str(doc_list)
    "[Document(metadata={}, page_content='d1'), Document(metadata={}, page_content='d2')]"

랭체인에서는 프롬프트에 문서를 반영할 때, 이렇게 문자열 표현을 사용하는 경우가 많습니다.

그런데, ``PaikdabangMenuDocument`` 쿼리셋을 문자열 표현으로 출력하면

.. code-block:: python

    >>> qs = PaikdabangMenuDocument.objects.all()
    >>> str(qs[:2])

다음과 같이 ``metadata`` 속성값과 ``page_content`` 속성값이 모두 표현되지 않습니다.

.. admonition:: 출력

    '<PaikdabangMenuDocumentQuerySet [<PaikdabangMenuDocument: PaikdabangMenuDocument object (1)>, <PaikdabangMenuDocument: PaikdabangMenuDocument object (2)>]>'

그럼 랭체인과 엮어서 사용할 경우, 아래와 같이 매번 리스트/사전 포맷으로 변환해야만 합니다.
변환하니까 문자열 표현에서 ``metadata`` 속성값과 ``page_content`` 속성값이 모두 잘 표현됩니다.

.. code-block:: python

    >>> qs = await PaikdabangMenuDocument.objects.search("빽다방 고카페인 음료 종류는?")
    >>> doc_list = [{"metadata": doc.metadata, "page_content": doc.page_content} for doc in qs]
    >>> str(doc_list)
    "[{'metadata': {'source': '빽다방.txt'}, 'page_content': '5. 빽사이즈 원조커피(ICED)\\n  - 빽다방 즐겨보세요 :) [주의. 564mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\\n  - 가격방.txt'}, 'page_content': '5. 빽사이즈 원조커피(ICED)\\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) [주어린이, 임산부는 섭취에 주의바랍니다]\\n  - 가격: 4000원'}, {'metadata': {'source': '빽다방.txt'}, 'page_피 제로슈거(ICED)\\n  - 빽다방의 BEST메뉴를 더 크게, 제로슈거로 즐겨보세요 :) [주의. 686mg 고카페인으로 카 - 가격: 4000원'}, {'metadata': {'source': '빽다방.txt'}, 'page_content': '6. 빽사이즈 원조커피 제로슈거(빽다방의 BEST메뉴를 더 크게, 제로슈거로 즐겨보세요 :) [주의. 686mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\\n  - 가격: 4000원'}]"

그런데 매번 리스트/사전 포맷으로 변환하는 것은 번거롭습니다.
``PaikdabangMenuDocumentQuerySet`` 클래스와 ``PaikdabangMenuDocument`` 클래스의 문자열 표현을 개선해보겠습니다.


QuerySet 클래스의 문자열 표현 개선
=========================================

``QuerySet`` 클래스에서는 문자열 표현에서 ``"<클래스명 데이터일부>"`` 포맷으로 생성토록 ``__repr__`` 메서드에 구현되어있습니다.

.. tip::

    파이썬 클래스 인스턴스에서는 ``repr(obj)`` 함수를 호출하면 ``__repr__`` 메서드가 호출되며, 
    ``str(obj)`` 함수를 호출하면 ``__str__`` 메서드가 있으면 호출되며, ``__str__`` 메서드가 없으면 ``__repr__`` 메서드가 호출됩니다.

``__repr__`` 메서드를 재정의하여, 리스트 포맷으로 문자열을 생성토록 합니다.

.. code-block:: python
    :emphasize-lines: 4-5

    class PaikdabangMenuDocumentQuerySet(models.QuerySet):
        # ...

        def __repr__(self):
            return repr(list(self))  # QuerySet을 리스트처럼 출력

그럼 쿼리셋의 문자열 표현이 리스트 포맷으로 생성됩니다.

.. admonition:: 출력

    '[<PaikdabangMenuDocument: PaikdabangMenuDocument object (1)>, <PaikdabangMenuDocument: PaikdabangMenuDocument object (2)>]'


모델 클래스의 문자열 표현 개선
======================================

모델 인스턴스의 문자열 표현은 ``"<PaikdabangMenuDocument: PaikdabangMenuDocument object (1)>"`` 입니다.
모델 클래스에는 ``__repr__`` 메서드와 ``__str__`` 메서드가 아래와 같이 재정의되어있기 때문입니다.

.. code-block:: python

    class Model(...):
        # ...

        def __repr__(self):
            return "<%s: %s>" % (self.__class__.__name__, self)

        def __str__(self):
            return "%s object (%s)" % (self.__class__.__name__, self.pk)

``PaikdabangMenuDocument`` 모델 클래스의 두 메서드를 아래와 같이 재정의해주세요.
``__repr__`` 메서드에서는 ``metadata`` 속성값과 ``page_content`` 속성값을 모두 표현하도록 하고,
``__str__`` 메서드에서는 ``__repr__`` 메서드를 호출하도록 합니다.

.. code-block:: python

    class PaikdabangMenuDocument(LifeCycleModelMixin, models.Model):
        # ...

        def __repr__(self):
            return f"Document(metadata={self.metadata}, page_content={self.page_content!r})"

        def __str__(self):
            return self.__repr__()

이제 문서의 쿼리셋이나 문서 인스턴스를 문자열 표현에서 ``metadata`` 속성값과 ``page_content`` 속성값이 모두 잘 표현됨을 확인하실 수 있습니다.

.. code-block:: python

    >>> doc_list = await PaikdabangMenuDocument.objects.search("빽다방 고카페인 음료 종류는?")
    >>> prompt = f"넌 AI Assistant. 모르는 건 모른다고 대답.\n\n[[빽다방 메뉴 정보]]\n{doc_list}"
    >>> prompt


.. admonition:: 생성된 문자열

    "넌 AI Assistant. 모르는 건 모른다고 대답.\n\n[[빽다방 메뉴 정보]]\n[Document(metadata={'source': '빽다방.txt'}, page_content='5. 빽사이 BEST메뉴를 더 크게 즐겨보세요 :) [주의. 564mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\\n  - 가격: 4000원'), Document='5. 빽사이즈 원조커피(ICED)\\n  - 빽다방의 BEST메뉴를 더 크게 즐겨보세요 :) [주의. 564mg 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]source': '빽다방.txt'}, page_content='6. 빽사이즈 원조커피 제로슈거(ICED)\\n  - 빽다방의 BEST메뉴를 더 크게, 제로슈거로 즐겨보세요 :) [주의. 686mg 고카페인으 가격: 4000원'), Document(metadata={'source': '빽다방.txt'}, page_content='6. 빽사이즈 원조커피 제로슈거(ICED)\\n  - 빽다방의 BEST메뉴를 더 크게 고카페인으로 카페인에 민감한 어린이, 임산부는 섭취에 주의바랍니다]\\n  - 가격: 4000원')]"


이제 랭체인 프롬프트에서도 간편하게 쿼리셋과 문서 인스턴스를 사용하실 수 있습니다. 😉
