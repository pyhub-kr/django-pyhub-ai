====================================
💬 장고로 만드는 RAG 웹 채팅 서비스
====================================

    AI 시대에 데이터는 모든 서비스의 핵심 자산입니다.

    이 튜토리얼은 파이썬/장고 기반으로 여러분의 데이터를 체계적으로 저장하고, 효율적으로 관리하며,
    RAG(Retrieval-Augmented Generation) 기술을 통해 AI 서비스와 연결하는 방법을 배우게 됩니다.
    장고의 강력한 ORM과 웹 프레임워크 기능을 활용하여 데이터 관리의 생산성을 높이고,
    LLM의 잠재력을 최대한 활용한 웹 채팅 서비스를 함께 만들어봅시다! 😉

    물론 LangChain/LangGraph 코드에도 장고 모델을 넣어서 사용하실 수 있어요.

.. admonition:: 튜토리얼 목적
    :class: note

    파이썬/장고 기반으로 손쉬운 문서/임베딩 관리 + 쉽고 간결한 애플리케이션 구현

    파이썬/장고와 함께 여러분의 데이터/도구를 직접 관리/개발하세요. ;-)

:doc:`/rag-02/index` 튜토리얼에서 다뤘던 내용을 보완해서, "파이썬 문법이 익숙한 웹/LLM 초보 개발자" 대상으로 재구성했습니다.
``django-pyhub-rag`` 라이브러리를 개발/활용하여 파이썬/장고 중심으로 생산성 높은 RAG 웹 채팅 서비스를 구현합니다.

* 장고 모델을 활용한 임베딩 생성/저장 및 유사도 검색 (코사인 거리)

  - SQLite/PostgreSQL 데이터베이스를 같은 모델 코드로 지원
  - 모델 클래스 상속 만으로 문서 데이터베이스 테이블 생성

* 채팅방 기본 화면 구성 (생성/목록, 채팅)
* HTMX를 활용한 채팅 UI 구현
* LLM 채팅에 RAG 붙이기


.. admonition:: 최종 결과 화면 미리보기
    :class: dropdown

    .. figure:: ./assets/anthropic/anthropic-response.png


오시기 전에
-------------------------------

* 소스코드 저장소 : https://github.com/pyhub-kr/django-webchat-rag-langcon2025

* :doc:`./preparation`


핸즈온랩
-----------------

* :doc:`./check`
* :doc:`./initial-project`
* :doc:`./app-models`
* :doc:`./load-data`
* :doc:`./search`
* :doc:`./rag-cli`
* :doc:`./chat-room`
* :doc:`./web-chat-using-form`
* :doc:`./web-chat-using-htmx`
* :doc:`./web-rag-chat`
* :doc:`./closing`

* 부록

  - :doc:`./styles-bubble`
  - :doc:`./styles-markdown`
  - :doc:`./styles-loading-indicator`
  - :doc:`./anthropic`

----

.. toctree::
    :maxdepth: 1
    :caption: 목차

    preparation
    check
    initial-project
    app-models
    load-data
    search
    rag-cli
    chat-room
    web-chat-using-form
    web-chat-using-htmx
    web-rag-chat
    closing
    styles-bubble
    styles-markdown
    styles-loading-indicator
    anthropic
