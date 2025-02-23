===========================
웹 채팅 UI (Form 활용)
===========================
  

메시지 전송 뷰
=================

.. code-block:: python
    :linenos:
    :caption: ``chat/views.py`` 파일에 추가

    from django.shortcuts import redirect, render, get_object_or_404
    from .forms import MessageForm

    def message_new(request, room_pk):
        room = get_object_or_404(Room, pk=room_pk)

        if request.method == "POST":
            form = MessageForm(data=request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.room = room
                message.save()
                # AI 응답 생성
                ai_message = message.create_ai_message()
                return redirect("chat:room_detail", pk=room_pk)
        else:
            form = MessageForm()

        return render(
            request,
            "chat/message_form.html",
            {
                "room": room,
                "form": form,
            },
        )


.. code-block:: python
    :linenos:
    :caption: ``chat/urls.py`` 파일에 추가
    :emphasize-lines: 10

    from django.urls import path
    from . import views

    app_name = "chat"

    urlpatterns = [
        path("", views.room_list, name="room_list"),
        path("new/", views.room_new, name="room_new"),
        path("<int:pk>/", views.room_detail, name="room_detail"),
        path("<int:room_pk>/messages/new/", views.message_new, name="message_new"),
    ]


간소화한 room_detail.html 템플릿 코드
============================================

.. code-block:: html+django
    :linenos:
    :caption: ``chat/templates/chat/room_detail.html`` 파일 수정
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

.. note::

    TODO: 화면이 전환되며 메시지가 추가되는 것을 GIF 이미지로 캡처하기

.. figure:: ./assets/web-chat-using-form.png
