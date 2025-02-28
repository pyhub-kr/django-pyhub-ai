====================================
부록 #1. 채팅 스타일 개선
====================================


대화 풍선 스타일 개선
============================

tailwind css 계열 CSS 라이브러리 중에 daisyui의 `chat bubble 컴포넌트 <https://daisyui.com/components/chat/>`_\를 적용해보겠습니다.

.. tab-set::

    .. tab-item:: 이전

        .. figure:: ./assets/styles/daisyui-chat-bubble-01.png

    .. tab-item:: 개선

        .. figure:: ./assets/styles/daisyui-chat-bubble-02.png

.. admonition:: ``chat/templates/chat/base.html`` 파일 덮어쓰기
    :class: dropdown

    .. code-block:: html+django
        :linenos:
        :emphasize-lines: 7-8

        <!doctype html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{% block title %}Django Chat{% endblock %}</title>
            {# https://daisyui.com/docs/cdn/ #}
            <link href="https://cdn.jsdelivr.net/npm/daisyui@4.12.24/dist/full.min.css" rel="stylesheet" type="text/css" />
            <script src="https://cdn.tailwindcss.com"></script>
            <script src="https://unpkg.com/htmx.org"></script>
            <script src="https://unpkg.com/alpinejs"></script>
        </head>
        <body class="bg-gray-100">
            <div class="container mx-auto px-4 py-8">
                <header class="mb-8">
                    <nav class="bg-white shadow-lg rounded-lg">
                        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                            <div class="flex justify-between h-16">
                                <div class="flex">
                                    <div class="flex-shrink-0 flex items-center">
                                        <a href="{% url 'chat:room_list' %}" class="text-xl font-bold text-gray-800">
                                            Django Chat
                                        </a>
                                    </div>
                                </div>
                                <div class="flex items-center">
                                    <a href="{% url 'chat:room_new' %}"
                                    class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
                                        새 채팅방
                                    </a>
                                </div>
                            </div>
                        </div>
                    </nav>
                </header>

                <main class="bg-white shadow-lg rounded-lg p-6">
                    {% block content %}
                    {% endblock %}
                </main>

                <footer class="mt-8 text-center text-gray-600 text-sm">
                    <p>&copy; 2025 파이썬사랑방. All rights reserved.</p>
                </footer>
            </div>
        </body>
        </html>

.. admonition:: ``chat/templates/chat/_message_list.html`` 파일 덮어쓰기
    :class: dropdown

    .. code-block:: html+django
        :linenos:

        {# https://daisyui.com/components/chat/ #}

        {% for message in message_list %}
            {% if message.role == "user" %}
                <div class="chat chat-start">
                    <div class="chat-bubble">
                        {{ message.content }}
                    </div>
                </div>
            {% else %}
                <div class="chat chat-end">
                    <div class="chat-bubble">
                        {{ message.content }}
                    </div>
                </div>
            {% endif %}
        {% endfor %}


markdown 포맷 변환
============================

markdown to html 변환은 서버 단에서 해도 되고, 클라이언트 단에서 해도 됩니다.
서버 단에서 수행하면 보다 풍부한 포맷 변환이 가능하지만, markdown 변환은 클라이언트 단에서 수행해도 충분할 듯 보입니다.

여러 라이브러리가 있지만 `Showdown <https://showdownjs.com/>`_ 라이브러리를 적용해보겠습니다.

.. figure:: ./assets/styles/markdown.png

.. admonition:: ``chat/templates/chat/base.html`` 파일 덮어쓰기
    :class: dropdown

    .. code-block:: html+django
        :linenos:
        :emphasize-lines: 1,12-14

        {% load static %}

        <!doctype html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{% block title %}Django Chat{% endblock %}</title>
            <link href="https://cdn.jsdelivr.net/npm/daisyui@4.12.24/dist/full.min.css" rel="stylesheet" type="text/css" />
            <script src="https://cdn.tailwindcss.com"></script>
            <script src="https://unpkg.com/htmx.org"></script>
            <script src="https://unpkg.com/alpinejs"></script>
            <script src="{% static 'rag/showdown/2.1.0/showdown.js' %}"></script>
            <script src="{% static 'rag/markdown.js' %}"></script>
        </head>
        <body class="bg-gray-100">
            <div class="container mx-auto px-4 py-8">
                <header class="mb-8">
                    <nav class="bg-white shadow-lg rounded-lg">
                        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                            <div class="flex justify-between h-16">
                                <div class="flex">
                                    <div class="flex-shrink-0 flex items-center">
                                        <a href="{% url 'chat:room_list' %}" class="text-xl font-bold text-gray-800">
                                            Django Chat
                                        </a>
                                    </div>
                                </div>
                                <div class="flex items-center">
                                    <a href="{% url 'chat:room_new' %}"
                                    class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
                                        새 채팅방
                                    </a>
                                </div>
                            </div>
                        </div>
                    </nav>
                </header>

                <main class="bg-white shadow-lg rounded-lg p-6">
                    {% block content %}
                    {% endblock %}
                </main>

                <footer class="mt-8 text-center text-gray-600 text-sm">
                    <p>&copy; 2025 파이썬사랑방. All rights reserved.</p>
                </footer>
            </div>
        </body>
        </html>

.. admonition:: ``chat/templates/chat/_message_list.html`` 파일 덮어쓰기
    :class: dropdown

    .. code-block:: html+django
        :linenos:
        :emphasize-lines: 1,11-23

        {% load rag_tags %}

        {% for message in message_list %}
            {% if message.role == "user" %}
                <div class="chat chat-start">
                    <div class="chat-bubble">
                        {{ message.content }}
                    </div>
                </div>
            {% else %}
                {# uuid4 포맷의 랜덤 id 발행 #}
                {% uuid4_id as message_id %}
                {# 지정 id로 메시지 문자열을 json 변환 #}
                {{ message.content|json_script:message_id }}
                <div class="chat chat-end">
                    <div class="chat-bubble"
                        x-data
                        x-init="
                            const jsonString = JSON.parse(document.getElementById('{{ message_id }}').textContent);
                            $el.innerHTML = markdownToHtml(jsonString);
                        ">
                    </div>
                </div>
            {% endif %}
        {% endfor %}


응답 대기 중 표시
============================

.. figure:: ./assets/styles/loading-indicator.gif

.. admonition:: ``chat/templates/chat/room_detail.html`` 파일 덮어쓰기
    :class: dropdown

    .. code-block:: html+django
        :linenos:
        :emphasize-lines: 5,13-21,24-26,32-35

        {% extends "chat/base.html" %}

        {% block content %}
        <div class="flex flex-col h-[calc(100vh-16rem)]"
            x-data="{ loading: false }">
            <div class="bg-white rounded-lg shadow-md p-4 mb-4">
                <h1 class="text-2xl font-bold text-gray-800">{{ room.name }}</h1>
                <p class="text-sm text-gray-600">생성일: {{ room.created_at|date:"Y-m-d H:i" }}</p>
            </div>

            <div class="flex-1 overflow-hidden">
                <div class="chat-messages h-full overflow-y-auto pb-2 overscroll-contain"
                    x-data="{
                        scrollToBottom() {
                            setTimeout(() => {
                                $el.scrollTo({ top: $el.scrollHeight, behavior: 'smooth'})
                            });
                        }
                    }"
                    x-init="scrollToBottom()"
                    @htmx:after-settle="scrollToBottom()">
                    {% include "chat/_message_list.html" with message_list=message_list only %}

                    <div x-show="loading" class="text-center py-2 text-gray-600">
                        응답 대기 중 ...
                    </div>
                </div>

            </div>

            <form hx-post="{% url 'chat:message_new' room_pk=room.pk %}"
                hx-target="previous .chat-messages"
                hx-swap="beforeend"
                @htmx:before-request="loading = true; $el.reset()"
                @htmx:after-request="loading = false" novalidate class="mt-4">
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
