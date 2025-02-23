==================================
웹 채팅 UI (HTMX 활용하여 개선)
==================================

.. figure:: ./assets/web-chat-using-htmx.png


.. code-block:: html+django
    :linenos:
    :caption: ``chat/templates/chat/_message_list.html`` 파일 생성

    {% for message in message_list %}
        <div>[{{ message.role }}] : {{ message.content }}</div>
    {% endfor %}


.. code-block:: html+django
    :linenos:
    :caption: ``chat/templates/chat/room_detail.html`` 파일 수정
    :emphasize-lines: 12,16-19

    {% extends "chat/base.html" %}

    {% block content %}
    <div class="flex flex-col h-[calc(100vh-16rem)]">
        <div class="bg-white rounded-lg shadow-md p-4 mb-4">
            <h1 class="text-2xl font-bold text-gray-800">{{ room.name }}</h1>
            <p class="text-sm text-gray-600">생성일: {{ room.created_at|date:"Y-m-d H:i" }}</p>
        </div>

        <div id="messages-container">
            <div id="chat-messages">
                {% include "chat/_message_list.html" with message_list=message_list %}
            </div>
        </div>

        <form hx-post="{% url 'chat:message_new' room_pk=room.pk %}"
              hx-target="#chat-messages"
              hx-swap="beforeend"
              hx-on::before-request="this.reset()"
              novalidate>
            {% csrf_token %}
            <div class="flex gap-2">
                <input type="text" name="content" required autocomplete="off" placeholder="메시지를 입력하세요..." autofocus
                    class="flex-1 bg-gray-100 rounded-lg px-4 py-2">
                <button type="submit"
                    class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition-colors duration-300">
                    전송
                </button>
            </div>
        </form>
    </div>
    {% endblock %}

.. code-block:: python
    :linenos:
    :caption: ``chat/views.py`` 파일 수정
    :emphasize-lines: 10-15

    def message_new(request, room_pk):
        room = get_object_or_404(Room, pk=room_pk)
        if request.method == "POST":
            form = MessageForm(data=request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.room = room
                message.save()
                ai_message = message.create_ai_message()
                # return redirect("chat:room_detail", pk=room_pk)
                return render(
                    request,
                    "chat/_message_list.html",
                    {"message_list": [message, ai_message]},
                )
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


