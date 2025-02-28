================================================================
📝 HTML Form과 장고 Form을 활용한 채팅 메시지 전송 및 응답
================================================================


.. admonition:: `관련 커밋 <https://github.com/pyhub-kr/django-webchat-rag-langcon2025/commit/5f2095926ad34426876cb56e4f5364d6cde83d47>`_
   :class: dropdown

   * 변경 파일을 한 번에 덮어쓰기 하실려면, :doc:`/utils/pyhub-git-commit-apply` 설치하신 후에, 프로젝트 루트에서 아래 명령 실행하시면
     지정 커밋의 모든 파일을 다운받아 현재 경로에 덮어쓰기합니다.

   .. code-block:: bash

      python -m pyhub_git_commit_apply https://github.com/pyhub-kr/django-webchat-rag-langcon2025/commit/5f2095926ad34426876cb56e4f5364d6cde83d47

   ``uv``\를 사용하실 경우 

   .. code-block:: bash

      uv run pyhub-git-commit-apply https://github.com/pyhub-kr/django-webchat-rag-langcon2025/commit/5f2095926ad34426876cb56e4f5364d6cde83d47


채팅 메시지 전송 뷰
======================

새로운 채팅 메시지를 전송받을 View를 전통적인 장고 Form 패턴으로 구현합니다.

* HTML 폼 요청에서는 ``GET`` 요청과 ``POST`` 요청 2가지만 존재합니다. ``GET`` 요청은 조회 목적으로만 사용하며, 생성/수정/삭제 요청은 항상 ``POST`` 요청으로 받습니다.
* 요청의 파일 데이터는 ``request.FILES`` 속성을 통해 참조할 수 있으며, 그 외 POST 데이터는 ``request.POST`` 속성을 통해 참조할 수 있습니다.
* 요청 데이터에 대한 유효성 검사는 장고 Form 인스턴스를 생성하고, ``.is_valid()`` 메서드를 호출하여 수행합니다. 단 하나의 유효성 검사라도 실패하면 ``False``\를 반환합니다.

  - 🔥 중요: 클라이언트로부터 전달받은 데이터는 절대 신뢰해서는 안 됩니다. 당연히 잘 맞춰 전달했을 것이라 가정해서는 안 됩니다. 반드시 유효성 검사를 수행하여 데이터 값/포맷/타입 등을 확인해야 합니다. 프론트엔드 단에서 입력값을 잘 구성해서 보냈다하더라도, 누군가 악의적인 목적으로 중간에 값을 변조할 수 있습니다. **장고 Form을 통해 효율적으로 유효성 검사를 수행할 수 있습니다.**

* 유효성 검사에 통과하면, 모델 폼을 통해 데이터베이스에 저장하고, AI 메시지를 생성한 후에 채팅방 페이지로 이동시킵니다.

  - 1개의 채팅 메시지를 받고 페이지를 이동시키는 UI가 좋은 경험은 아닙니다. 하지만 이는 **장고를 효율적으로 활용한 생산성 높은 개발 방법**\입니다.
  - 다음 :doc:`./web-chat-using-htmx` 문서에서 자바스크립트 없이도 장고 중심으로 효율적으로 UX를 향상시킬 수 있는 방법을 소개합니다.

* 유효성 검사에 실패하면, 에러 메시지와 함께 에러 HTML 폼 화면을 응답합니다.

.. code-block:: python
    :linenos:
    :caption: ``chat/views.py`` 파일 덮어쓰기
    :emphasize-lines: 1,3,4,6,58-80

    from django.shortcuts import get_object_or_404, render, redirect
    from django.urls import reverse_lazy
    from django.views.decorators.http import require_POST
    from django.views.generic import ListView, CreateView

    from .forms import RoomForm, MessageForm
    from .models import Room, TaxLawDocument


    # 채팅방 목록 페이지 (클래스 기반 뷰)
    room_list = ListView.as_view(model=Room)


    # 새 채팅방 생성 페이지 (클래스 기반 뷰)
    room_new = CreateView.as_view(
        model=Room,
        form_class=RoomForm,
        success_url=reverse_lazy("chat:room_list"),
    )


    # 채팅방 채팅 페이지 (함수 기반 뷰)
    def room_detail(request, pk):
        # 지정 채팅방 조회하고, 데이터베이스에 없으면 404 오류 발생
        room = get_object_or_404(Room, pk=pk)
        # 지정 채팅방의 모든 대화 목록
        message_list = room.message_set.all()
        return render(
            request,
            "chat/room_detail.html",
            {
                "room": room,
                "message_list": message_list,
            },
        )


    # 문서 검색 페이지
    class TaxLawDocumentListView(ListView):
        model = TaxLawDocument
        # sqlite의 similarity_search 메서드가 쿼리셋이 아닌 리스트를 반환하기 때문에
        # ListView에서 템플릿 이름을 찾지 못하기에 직접 지정해줍니다.
        template_name = "chat/taxlawdocument_list.html"

        def get_queryset(self):
            qs = super().get_queryset()

            query = self.request.GET.get("query", "").strip()
            if query:
                qs = qs.similarity_search(query)  # noqa: list 타입
            else:
                # 검색어가 없다면 빈 쿼리셋을 반환합니다.
                qs = qs.none()

            return qs


    # POST 요청 만을 허용합니다.
    @require_POST
    def message_new(request, room_pk):
        room = get_object_or_404(Room, pk=room_pk)

        form = MessageForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.room = room
            message.save()
            # 대화 목록에 기반해서 AI 응답 생성하고 데이터베이스에 저장합니다.
            # 방금 입력된 유저 메시지가 대화 기록 마지막에 추가되어 있습니다.
            ai_message = room.create_ai_message()
            return redirect("chat:room_detail", pk=room_pk)

        return render(
            request,
            "chat/message_form.html",  # 생성하지 않은 템플릿.
            {
                "room": room,
                "form": form,
            },
        )


방금 구현한 ``message_new`` 뷰를 호출하는 URL 패턴을 추가합니다.

.. code-block:: python
    :linenos:
    :caption: ``chat/urls.py`` 파일 덮어쓰기
    :emphasize-lines: 10

    from django.urls import path
    from . import views

    app_name = "chat"

    urlpatterns = [
        path("", views.room_list, name="room_list"),
        path("new/", views.room_new, name="room_new"),
        path("<int:pk>/", views.room_detail, name="room_detail"),
        path("<int:room_pk>/messages/new/", views.message_new, name="message_new"),
        path("docs/law/tax/", views.TaxLawDocumentListView.as_view()),
    ]


간소화한 room_detail.html 템플릿 코드
============================================

이전 문서에서 사용한 템플릿은 스타일이 복잡해서 코드를 간소화하여 예제를 진행하겠습니다.

* ``<form>`` 태그에 ``method="post"`` 속성을 추가하여 ``POST`` 방식으로 요청을 전송하고,
* ``action`` 속성으로 메시지를 전송할 주소를 지정합니다.
* ``novalidate`` 속성을 추가하여 브라우저의 기본 유효성 검사를 비활성화합니다.

.. code-block:: html+django
    :linenos:
    :caption: ``chat/templates/chat/room_detail.html`` 파일 덮어쓰기
    :emphasize-lines: 18

    {% extends "chat/base.html" %}

    {% block content %}
    <div class="flex flex-col h-[calc(100vh-16rem)]">
        <div class="bg-white rounded-lg shadow-md p-4 mb-4">
            <h1 class="text-2xl font-bold text-gray-800">{{ room.name }}</h1>
            <p class="text-sm text-gray-600">생성일: {{ room.created_at|date:"Y-m-d H:i" }}</p>
        </div>

        <div id="messages-container">
            <div id="chat-messages">
                {% for message in message_list %}
                    <div>[{{ message.role }}] : {{ message.content }}</div>
                {% endfor %}
            </div>
        </div>

        <form method="post" action="{% url 'chat:message_new' room_pk=room.pk %}" novalidate>
            {% csrf_token %}
            <div class="flex gap-2">
                <input type="text" name="content" required autocomplete="off" placeholder="메시지를 입력하세요..."
                    autofocus class="flex-1 bg-gray-100 rounded-lg px-4 py-2">
                <button type="submit"
                    class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition-colors duration-300">
                    전송
                </button>
            </div>
        </form>
    </div>
    {% endblock %}

이렇게 브라우저 기본의 ``<form>`` 전송을 활용하여 채팅 메시지를 전송할 수 있습니다.
파일 업로드가 필요할 때에는 ``<form>`` 태그에 ``enctype="multipart/form-data"`` 속성을 추가하시면 브라우저에서 알아서 파일 전송까지 해줍니다.
자바스크립트를 써야만 모던한 애플리케이션이 되는 것은 아닙니다.

.. note::

    ``room_detail.html`` 템플릿에서도 채팅메시지 입력폼 필드 렌더링을 장고 Form을 활용해서 구현할 수 있습니다.


동작 화면
================

위 내용을 모두 적용하고 채팅방에서 채팅 메시지를 입력하고 잠시 기다려보시면 이어서 채팅 응답을 받으시게 됩니다.

.. figure:: ./assets/web-chat-using-form/play.gif

페이지 전환이 발생했는 데 느끼셨나요? 워낙 빠르게 페이지가 전환되어 느끼기 어려울 수 있습니다.
``python manage.py runserver`` 명령어를 실행한 콘솔 출력 로그를 보시면 페이지 전환이 발생했음을 확인하실 수 있습니다.

.. code-block:: text

    [28/Feb/2025 06:11:32] "POST /chat/1/messages/new/ HTTP/1.1" 302 0
    [28/Feb/2025 06:11:32] "GET /chat/1/ HTTP/1.1" 200 16719

새로운 채팅 메시지를 ``/chat/1/messages/new/`` 주소로 ``POST`` 방식으로 보내며 페이지 전환이 발생했고,
서버에서 AI 응답 생성 후에 ``/chat/1/`` 주소로 이동하라는 ``302`` 응답을 보냈구요.
이에 브라우저는 ``/chat/1/`` 주소로 다시 이동을 한 상황입니다.
