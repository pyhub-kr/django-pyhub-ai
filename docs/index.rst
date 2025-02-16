파이썬사랑방 튜토리얼
=========================

LLM을 활용한 애플리케이션 개발에서 자주 언급되는 ``Streamlit`` 라이브러리는 LLM(대규모 언어 모델) 기반 웹서비스를 간결하게 구현하기에는 적합하지만, 웹서비스의 전반적인 확장성, 사용자 인증, 권한 관리, 그리고 복잡한 백엔드 로직 처리에는 제약이 있을 수 있습니다. 프로토타이핑이나 단순한 웹 애플리케이션 제작에는 유용하지만, 완전한 웹서비스 개발에는 한계가 있습니다.

반면, 장고는 20년의 역사와 강력한 생태계를 바탕으로, 파이썬 기반의 풀스택 웹프레임워크로서 서비스를 빠르고 안정적으로 개발할 수 있도록 돕고, 복잡한 웹서비스의 요구 사항을 충족시키기에 충분합니다.

다양한 튜토리얼을 개발하여, 더 많은 분들이 보다 쉽게 RAG/에이전트 기반 서비스를 개발하실 수 있도록 돕겠습니다.

* RAG 튜토리얼

  - :doc:`./rag-01/index` : RAG 초심자 분들에게 추천드립니다 ~ !!!
  - :doc:`./rag-02/index` : **실전 튜토리얼**\로서, 실제 서비스 개발에 많이 사용되어지는
    Postgres `pgvector <https://github.com/pgvector/pgvector>`_ 확장을
    장고 프로젝트에 통합하는 방법을 다룹니다.

* ``django-pyhub-ai`` 라이브러리를 활용한 LLM 에이전트 채팅 서비스 개발 튜토리얼

  - :doc:`./quickstart/index`

  - :doc:`./quickstart_02/index`

RAG/에이전트와 함께 여러분의 파이썬/장고 페이스메이커가 되겠습니다. 🥳

.. toctree::
   :maxdepth: 1
   :caption: 목차
   :hidden:

   rag-01/index
   rag-02/index
   quickstart/index
   quickstart_02/index
   consumers/index
   django/index
   setup/index
   utils/index
