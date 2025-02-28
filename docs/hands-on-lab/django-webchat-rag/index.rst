====================================
💬 장고로 만드는 RAG 웹 채팅 서비스
====================================

:doc:`/rag-02/index` 튜토리얼에서 다뤘던 내용을 보완해서, "파이썬 문법이 익숙한 웹/LLM 초보 개발자" 대상으로 재구성했습니다.
``django-pyhub-rag`` 라이브러리를 개발/활용하여 파이썬/장고 중심으로 생산성 높은 RAG 웹 채팅 서비스를 구현합니다.

* 장고 모델을 활용한 임베딩 생성/저장 및 유사도 검색 (코사인 거리)

  - SQLite/PostgreSQL 데이터베이스를 같은 모델 코드로 지원
  - 모델 클래스 상속 만으로 문서 데이터베이스 테이블 생성

* 채팅방 기본 화면 구성 (생성/목록, 채팅)
* HTMX를 활용한 채팅 UI 구현
* LLM 채팅에 RAG 붙이기


(랭콘 2025) 장고로 만드는 RAG 웹 채팅 서비스
====================================================

* 랭콘 2025 행사 링크 : https://event-us.kr/langcon/event/99194
* 시간 : 2025년 3월 1일, 오후 3시 50분 ~ 5시 20분
* 진행자 : 이진석 (`파이썬사랑방 커뮤니티 <https://facebook.com/groups/askdjango>`_ 운영자, `인프런 지식공유자 <https://www.inflearn.com/users/25058/@pyhub>`_\)
* 소스코드 저장소 : https://github.com/pyhub-kr/django-webchat-rag-langcon2025

오시기 전에
-------------------------------

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

  - :doc:`./styles`
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
    styles
    anthropic
