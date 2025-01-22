AI 응답 메시지에 markdown 변환 지원
=====================================


.. admonition:: `관련 커밋 <https://github.com/pyhub-kr/django-llm-chat-proj/commit/fd4d9109910c979e9fadc16b30ebc1518edbc9e1>`_
   :class: dropdown

   * 변경 파일을 한 번에 덮어쓰기 하실려면, :doc:`/utils/pyhub-git-commit-apply` 설치하신 후에, 현재 프로젝트 루트 경로에서 명령어 실행

   .. code-block:: bash

      uv run pyhub-git-commit-apply https://github.com/pyhub-kr/django-llm-chat-proj/commit/fd4d9109910c979e9fadc16b30ebc1518edbc9e1


미리보기
--------

대개의 LLM에서는 출력 포맷을 따로 요청하지 않으면, 대개 markdown 포맷으로 응답을 합니다.
markdown 포맷의 문자열은 plain text로서 웹 브라우저에서는 텍스트로 출력될 뿐 markdown 문법은 적용되지 않습니다.
markdown 포맷의 문자열은 HTML 코드로 변환하면, 웹 브라우저에서 스타일링이 적용되어 보기 좋게 출력됩니다.

.. tab-set::

   .. tab-item:: markdown → HTML 변환 전

      .. image:: ./assets/08-rag.png

   .. tab-item:: markdown → HTML 변환 후
      :selected:

      .. image:: ./assets/10-markdown.png


예시: markdown을 html로 변환하는 법
----------------------------------------

``markdown`` 문자열은 브라우저에서는 단순 텍스트입니다. 그래서 markdown 포맷을 살려 출력할려면 HTML 코드로 변환해야 합니다.

.. tab-set::

   .. tab-item:: markdown 그대로 노출

      .. code-block:: html

          <div>
          # 제목
          ## 소제목
          - 목록
          - 목록
          </div>

      .. image:: ./assets/10-markdown-raw.png
        :height: 60px

   .. tab-item:: HTML로 변환 후의 DOM 상황

       .. code-block:: html

          <div>
              <h1 id="">제목</h1>
              <h2 id="-1">소제목</h2>
              <ul>
                  <li>목록</li>
                  <li>목록</li>
              </ul>
          </div>

      .. image:: ./assets/10-markdown-html.png
         :height: 200px


``markdown to html`` 변환은 서버 단에서 해도 되고, 클라이언트 단에서 할 수도 있습니다.
``markdown`` 변환은 웹브라우저에서도 충분히 처리할 수 있으므로 웹브라우저에게 맡기도록 하겠습니다.
다양한 변환 라이브러리가 있겠지만 `showdown <https://showdownjs.com>`_ 라이브러리를 사용해보겠습니다.

``showdown`` 라이브러리를 사용하여, 웹페이지에서 아래와 같이 ``markdown`` 문자열을 ``html`` 코드로 변환하실 수 있습니다.

#. ``markdown`` 문자열은 화면에서 숨겨두고, 자바스크립트를 통해 ``markdown`` 문자열만 추출합니다.
#. ``showdown`` 라이브러리를 통해 ``markdown`` 문자열을 ``html`` 코드로 변환합니다.
#. 변환된 ``html`` 문자열을 노출시킬 요소에 반영하여 출력합니다.

.. code-block:: html

    <script src="//unpkg.com/showdown"></script>

    <div id="markdown-text" style="display: none;">
    # 제목
    ## 소제목
    - 목록
    - 목록
    </div>

    <div id="markdown-html"></div>

    <script>
        const markdownText = document.getElementById("markdown-text").textContent;
        const converter = new window.showdown.Converter({tables: true});
        const htmlText = converter.makeHtml(markdownText);
        document.getElementById("markdown-html").innerHTML = htmlText;
    </script>


markdown 변환 준비
--------------------

장고 프로젝트에 적용해보겠습니다.

장고에서는 css/javascript와 같은 정적 파일들을 ``static`` 리소스라 부릅니다.
``markdown`` 변환 함수는 여러 페이지에 걸쳐 사용될 수 있기에 ``static/markdown.js`` 경로에 정의했습니다.
아래 ``markdownToHtml`` 함수를 정의하지 않고, 바로 ``window.shotdown.Converter`` 객체를 사용할 수도 있겠지만
별도 함수로 두어 재사용성을 높이고 언제든 다른 ``markdown`` 변환 라이브러리로 교체할 수 있도록 합니다.

.. code-block:: javascript
   :caption: ``static/markdown.js``

    function markdownToHtml(text) {
        if (window.showdown?.Converter) {
            window.showdownConverter ||= new window.showdown.Converter({tables: true});
            return window.showdownConverter.makeHtml(text);
        }
        else {
            console.error('showdown library not found. Markdown to HTML conversion failed.');
            return text;
        }
    }

최상위 부모 레이아웃에서 ``showdown`` 라이브러리를 로드하고, ``markdown.js`` 파일을 로드합니다.
장고에서는 ``static`` 리소스에 대한 URL은 하드코딩으로 생성하지 않고 ``{% static %}`` 템플릿 태그를 통해 생성합니다.
이렇게 하면, ``static`` 파일이 있는 저장소가 변경되더라도 (로컬, AWS S3 등) 소스코드 수정 없이 ``settings`` 변경 만으로 대응할 수 있습니다.

.. code-block:: html+django
   :caption: ``templates/base.html``
   :emphasize-lines: 1,6

    {% load static %}

    {# ... #}

    <script src="//unpkg.com/showdown"></script>
    <script src="{% static 'markdown.js' %}"></script>


reply 응답 처리
--------------------

``reply`` 뷰에서 AI 응답 메시지를 자바스크립트까지 있어 복잡하므로, 아래와 같이 장고 템플릿 시스템을 통해 처리합니다.
HTMX를 통해서 서버 응답을 처리할 때 HTML 뿐만 아니라 alpine.js를 포함한 자바스크립트 코드까지 모두 자동 수행해주므로,
자바스크립트 코드를 통해 여러 동적인 처리를 할 수 있어, 활용도가 무궁무진 합니다.

.. code-block:: python
   :caption: ``chat/views.py``


    def reply(request):
        # ...
        return render(
            request,
            "chat/_chat_message.html",
            {
                "human_message": human_message,
                "ai_message": ai_message,
            },
        )

.. tab-set::

   .. tab-item:: 템플릿 코드

      .. code-block:: html+django
         :caption: ``chat/templates/chat/_chat_message.html``

         <div>
             <div class="chat chat-start">
                 <div class="chat-bubble">{{ human_message }}</div>
             </div>
             {# markdown 문자열은 숨겨둡니다. #}
             <div class="markdown hidden">{{ ai_message }}</div>
             <div class="chat chat-end">
                 {# 변환된 html 문자열을 노출시킬 요소입니다. #}
                 <div class="chat-bubble ai"></div>
             </div>
             <script>
             {# 웹페이지 내 다른 자바스크립트 코드와 변수 충돌을 막기 위해 #}
             {# 즉시 실행 함수로 작성하고, 함수 내 지역변수로 처리합니다. #}
             (() => {
                 const mdText = document.currentScript.parentElement.querySelector(".markdown")?.textContent;
                 const aiEl = document.currentScript.parentElement.querySelector(".ai");
                 // 이미 변환한 요소에 대해서 재변환을 하지 않도록 dataset 속성에 플래그를 남겨둡니다.
                 if (mdText && aiEl && !aiEl.dataset.mdProcessed) {
                     aiEl.innerHTML = window.markdownToHtml(mdText);
                     aiEl.dataset.mdProcessed = "true";
                 }
             })();
             </script>
         </div>

   .. tab-item:: alpine.js 버전

      alpine.js를 통해서도 동일하게 마크다운 변환을 수행할 수 있습니다.
      ``x-data`` 속성을 통해 데이터 속성 및 메서드를 정의하고,
      ``x-init`` 속성을 통해 초기화 코드를 정의합니다.

      .. code-block:: html+django
         :caption: ``chat/templates/chat/_chat_message.html``

         {# https://daisyui.com/components/chat/ #}
         <div x-data="{
                convert() {
                  const markdownText = this.$el.querySelector('.markdown')?.textContent || '';
                  const aiEl = this.$el.querySelector('.ai');
                  aiEl.innerHTML = window.markdownToHtml(markdownText);
                }
              }"
              x-init="convert();">

             <div class="chat chat-start">
                 <div class="chat-bubble">{{ human_message }}</div>
             </div>
             <div class="markdown hidden">{{ ai_message }}</div>
             <div class="chat chat-end">
                 <div class="chat-bubble ai"></div>
             </div>
         </div>
