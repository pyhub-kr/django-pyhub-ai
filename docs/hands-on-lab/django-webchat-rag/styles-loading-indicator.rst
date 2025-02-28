============================================
부록 #3. 응답 대기 중 표시
============================================

.. admonition:: `관련 커밋 <https://github.com/pyhub-kr/django-webchat-rag-langcon2025/commit/355aa3f0221992bd76501daffdf7ce7502c128a4>`_
   :class: dropdown

   * 변경 파일을 한 번에 덮어쓰기 하실려면, :doc:`/utils/pyhub-git-commit-apply` 설치하신 후에, 프로젝트 루트에서 아래 명령 실행하시면
     지정 커밋의 모든 파일을 다운받아 현재 경로에 덮어쓰기합니다.

   .. code-block:: bash

      python -m pyhub_git_commit_apply https://github.com/pyhub-kr/django-webchat-rag-langcon2025/commit/355aa3f0221992bd76501daffdf7ce7502c128a4

   ``uv``\를 사용하실 경우 

   .. code-block:: bash

      uv run pyhub-git-commit-apply https://github.com/pyhub-kr/django-webchat-rag-langcon2025/commit/355aa3f0221992bd76501daffdf7ce7502c128a4

.. figure:: ./assets/styles/loading-indicator.gif

.. admonition:: ``chat/templates/chat/room_detail.html`` 파일 덮어쓰기
    :class: dropdown

    .. code-block::
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
