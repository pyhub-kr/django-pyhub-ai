=====================================
부록 #1. 대화 풍선 스타일 개선
=====================================

.. admonition:: `관련 커밋 <https://github.com/pyhub-kr/django-webchat-rag-langcon2025/commit/3e4c211f2d5a39a6030a3b6a122e6d02c4e2c3ba>`_
   :class: dropdown

   * 변경 파일을 한 번에 덮어쓰기 하실려면, :doc:`/utils/pyhub-git-commit-apply` 설치하신 후에, 프로젝트 루트에서 아래 명령 실행하시면
     지정 커밋의 모든 파일을 다운받아 현재 경로에 덮어쓰기합니다.

   .. code-block:: bash

      python -m pyhub_git_commit_apply https://github.com/pyhub-kr/django-webchat-rag-langcon2025/commit/3e4c211f2d5a39a6030a3b6a122e6d02c4e2c3ba

   ``uv``\를 사용하실 경우 

   .. code-block:: bash

      uv run pyhub-git-commit-apply https://github.com/pyhub-kr/django-webchat-rag-langcon2025/commit/3e4c211f2d5a39a6030a3b6a122e6d02c4e2c3ba

대화내역 스타일이 너무 밋밋하죠? :-)
현재 사이트는 tailwind css이 너무 적용되어있습니다. 그래서 tailwind css 기반으로 직접 대화 메시지 스타일을 꾸미실 수도 있구요.
본 부록에서는 tailwind css 계열 CSS 라이브러리 중에 daisyui의 `chat bubble 컴포넌트 <https://daisyui.com/components/chat/>`_\를 적용하여
대화 메시지 스타일을 풍선 스타일로 빠르게 개선해보겠습니다.

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

