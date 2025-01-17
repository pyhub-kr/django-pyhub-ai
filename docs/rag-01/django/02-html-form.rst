HTML Form 기반으로 AI 응답 받기
================================


.. admonition:: `관련 커밋 <https://github.com/pyhub-kr/django-llm-chat-proj/commit/9b7aa6c24bc3c3d6ae800470951489e060da175a>`_
   :class: dropdown

   * 변경 파일을 한 번에 덮어쓰기 하실려면, :doc:`/utils/pyhub-git-commit-apply` 설치하신 후에, 현재 프로젝트 루트 경로에서 명령어 실행

   .. code-block:: bash

      uv run pyhub-git-commit-apply https://github.com/pyhub-kr/django-llm-chat-proj/commit/9b7aa6c24bc3c3d6ae800470951489e060da175a


장고 HTML 템플릿
-------------------

HTML에서는 유저에게 입력폼 UI를 제공하고, 입력폼을 통해 전송받은 값을 지정 주소의 Endpoint로 전송하는 기능을 제공합니다.

.. code-block:: html

   <form action="전송할_주소" method="요청방식">
       <input type="text" name="message" />
       <input type="submit" value="전송" />
   </form>

.. admonition:: 폼 전송에서 HTML <form> 적극 활용하세요.
   :class: tip
    
   HTML 사용을 최소화하고 자바스크립트를 활용하는 방법 만이 트렌디하고 모던한 방식인 것은 아닙니다.
   웹의 3대 언어는 HTML/CSS/JS 입니다. 특정 라이브러리에 갇히지 마시고, 웹을 하세요.
   견고하면서도 생산성을 극대화시킬 수 있는 방법을 고민하셔야 합니다.

   HTML <form>을 활용하면 보다 간결한 코드로 견고한 구현이 가능하며, 장고 Form 과도 궁합이 좋아 추가적인 에러 처리와 유효성 검사를 쉽게 설정할 수 있습니다.
   이를 통해 개발자는 자바스크립트로 작성해야 할 코드를 줄이고, 보다 안정적이고 유지보수하기 쉬운 구조를 만들 수 있습니다.
   물론 세련되고 편리한 UI도 구현할 수 있어 모던한 개발 요구에도 충분히 부합합니다.

``chat/templates/chat/index.html`` 파일을 열어서 아래와 같이 변경해주세요.

* ``action`` : 입력폼 데이터를 전송할 주소입니다. ``/chat/reply/`` 값을 입력하면 현재 웹페이지 주소의 ``/chat/reply/`` 주소로 전송됩니다.
* ``method`` : 입력폼 데이터를 전송할 방식입니다.

  - ``GET`` 과 ``POST`` 만을 지원합니다.
  - ``GET`` 방식 : 대개 조회 목적으로 사용. 파일 업로드 불가 (엽서 방식에 비유)
  - ``POST`` 방식 : 대개 조회 이외의 목적으로 사용 (생성/수정/삭제 등). 파일 업로드 가능 (택배 방식에 비유)

* ``{% csrf_token %}``

  - 장고 기본에서 제공해주는 보안 기능으로서 CSRF 공격 (사이트 간 요청 위조)을 막아 줍니다.
  - 장고 템플릿 태그로서 ``<input type="hidden" name="csrfmiddlewaretoken" value="zYMfHs2bzQI3LbJGkTjdwlH35VdxjCdZxWKBl7S53wDrsZFr4Jc3L6ZCWAezRuRC" />`` 태그를 자동으로 생성합니다. 폼 POST 전송 시에 유저 입력 값과 함께 전송되어, 장고는 요청의 유효성을 검증하고 CSRF 공격을 자동으로 방어합니다.

자바스크립트 웹소켓 API를 호출했던 ``<script>`` 태그는 제거해주세요. 지금은 ``<form>`` 태그를 통해서만 요청을 처리하고 점진적으로 개선해보겠습니다.

.. code-block:: html
   :caption: chat/templates/chat/index.html

   <form id="form" action="/chat/reply/" method="POST">
       {% csrf_token %}
       <input type="text" name="message" />
   </form>

   <div id="messages"></div>

   <!-- script 태그는 모두 제거합니다. -->

.. admonition:: 절대 장고의 CSRF 보호 기능을 끄지 마세요.
   :class: caution

   잘 모르시고 CSRF 보호 기능을 끄시는 분들을 종종 봅니다. 절대 끄지 마세요.

   CSRF Token 값은 ``<form>`` 에서는 ``{% csrf_token %}`` 만 쓰시면 되고, ``csrftoken`` 쿠키를 통해서도 조회하실 수 있어 JS를 통한 HTTP 요청에서도 손쉽게 조회하실 수 있습니다.
   이렇게 POST 전송 시에 유저 입력값과 함께 전송된 csrf token은 장고 미들웨어 단에서 요청의 유효성을 검증하고 CSRF 공격을 자동으로 방어합니다.

   신경쓰실 부분이 거의 없습니다. 끄지 마시고 꼭 써주세요.
   보안 기능은 서비스를 느리게 만드는 것이 아니라 안전하게 만들어줍니다.



View 구현
----------

장고에서는 HTTP 요청을 ``View`` 함수를 통해 처리합니다.

.. code-block:: python

   from django.http import HttpRequest, HttpResponse

   def reply(request: HttpRequest) -> HttpResponse:
       # request를 통해 모든 요청 내역을 조회할 수 있습니다.
       # 요청을 처리하고 응답 내용을 생성한 후
       # 반드시 HttpResponse 객체로 응답해야만 합니다.
       return HttpResponse("hello world")  # 텍스트, 이미지, PDF 등 다양한 응답 가능


.. admonition:: View를 구현하는 2가지 방법
   :class: important

   장고에서는 2가지 방식의 View를 제안합니다.

   1. 함수로 View를 구현하는 함수 기반 뷰 (FBV, Function Based View)
   2. 클래스로 View를 구현하는 클래스 기반 뷰 (CBV, Class Based View)


   함수는 함수 내 특정 루틴을 변경할 수 없습니다. 그 함수 전체를 재정의할 수 밖에 없죠.
   반면 클래스는 상속을 통해 특정 메서드의 동작을 변경할 수 있고, 다중 상속을 통해 여러 메서드들을 손쉽게 조합할 수 있습니다.
   
   여러 View를 구현하다보면, 여러 View에 걸쳐 반복되는 코드가 필연적입니다. 몇몇 View를 제외하고는 거의 동일한 패턴일 것입니다.
   이런 중복을 줄이기 위해서 클래스 기반 뷰가 설계되었습니다. 클래스 기반 뷰는 클래스를 통해 함수를 생성하는 방식입니다.
   클래스 기반 뷰를 활용하시면 많은 View 코드는 설정에 가까운 코드로 구현하실 수 있습니다.
   물론 메서드를 재정의해서 입맛대로 동작을 변경하실 수도 있습니다.
   하지만 함수 기반 뷰에 대한 이해가 없으면 클래스 기반 뷰를 이해하지 못하고 응용을 하실 수 없습니다.
   그리고는 "장고 클래스 기반 뷰"는 정해진 몇몇 용처로 밖에 사용하지 못한다고 오해하시곤 합니다.

   View 학습의 기본은 함수 기반 뷰입니다. 함수 기반 뷰로 "장고 View"의 기초를 닦으시고, 클래스 기반 뷰를 통해 중복을 줄여가세요.
   기본 클래스 기반 뷰를 넘어, 여러분들만의 클래스 기반 뷰를 개발하고 쌓아가세요.  
   개발 생산성 향상의 코어가 되어드릴 것입니다.


``/chat/reply/`` HTTP ``POST`` 요청	만을 처리하는 View를 구현합니다. 아직 LLM API를 호출하지는 않구요. 단순히 유저로부터 받은 메시지가 몇 글자인지로만 응답하겠습니다.

.. code-block:: python
   :caption: chat/views.py

   from django.http import HttpResponse
   from django.utils.html import format_html

   def reply(request):
       # request.method 속성 값은 "POST" 또는 "GET" 중 하나입니다. (항상 대문자)
       if request.method == "POST":
           human_message = request.POST.get("message", "")
           ai_message = f"입력하신 메시지는 {len(human_message)} 글자입니다."
           return HttpResponse(
               format_html(
                   "<div>[Human] {}</div><div>[AI] {}</div>", human_message, ai_message
               )
           )
       # GET 요청일 경우에는 허용하지 않는 메서드라고 응답합니다.
       else:
           return HttpResponse("<div>허용하지 않는 메서드</div>")

.. note::

   사용자가 입력한 메시지에 악의적인 목적으로 HTML 태그나 자바스크립트 코드가 포함될 수 있으므로, 안전하게 메시지를 출력하기 위해 ``format_html`` 함수를 활용했습니다.

   * 이 함수를 사용하면, 예를 들어 ``<script>alert("hello");</script>`` 와 같은 코드는 ``&lt;script&gt;alert(&quot;hello&quot;);&lt;/script&gt;`` 로 변환됩니다. 이를 통해 브라우저에서 해당 내용이 태그로 동작하지 않고, 단순한 텍스트로 화면에 표시됩니다.
   * 반대로 ``format_html`` 을 사용하지 않고 사용자 입력 메시지를 그대로 출력하면, 다른 사용자에게 자바스크립트 코드가 실행되어 알림창이 뜨는 등의 문제가 발생할 수 있습니다. 유저 입력값을 화면에 표시할 때에는 반드시 ``format_html`` 을 사용하세요.

.. important::
   
   **중요: 🔥 클라이언트로부터 전달받은 값은 절대 신뢰해서는 안 됩니다.**

   빠른 구현을 위해 요청 데이터에 대해서 유효성 검사를 수행하지 않고, 바로 값을 사용했습니다.
   서비스에서는 요청 데이터에 대해서 유효성 검사를 수행해야 합니다.

   * "당연히 유저가 잘 입력했겠지". 라고 생각해서는 절대 안 됩니다.
   * "웹 프론트엔드 단에서 유효성 검사를 했으니 백엔드 단에서는 유효성 검사를 안해도 되겠지." 라고 생각해서는 절대 안 됩니다.

   서버 외부에서 전달받은 값은 변조될 수 있고, 또는 악의적인 목적으로 흉내내어 전달될 수 있습니다.

   항상 값을 검사해야만 합니다. 이때 `장고 Form <https://docs.djangoproject.com/en/dev/topics/forms/>`_\ 을 활용하시면 편리하고 안전합니다.


URL 패턴 등록
--------------

구현한 ``reply`` View 함수에 URL 매핑을 추가합니다.

.. code-block:: python
   :caption: chat/urls.py

   # ...

   urlpatterns = [
       # ...
       path("reply/", views.reply, name="reply"),
   ]

이제 ``/chat/reply/`` 요청에 대해서는 ``reply`` View 함수가 매번 호출되어 처리됩니다.


동작 테스트
------------

`http://localhost:8000/chat/ <http://localhost:8000/chat/>`_ 주소로 접속해서 입력폼을 띄우시고, 입력폼을 전송해보세요.
페이지가 ``/chat/reply/`` 주소로 이동하면서 입력폼에서 전달받은 값이 처리되었음을 확인할 수 있습니다.

.. tab-set::

   .. tab-item:: 입력폼

      .. image:: ./assets/02-html-form-01.png

   .. tab-item:: 전송후

      .. image:: ./assets/02-html-form-02.png

HTML Form이 전송되며 웹페이지가 전환되었는 데요. 채팅 UI 구현을 위해서는 페이지 전환없이 요청을 하고 응답을 받아 처리할 수 있어야 합니다.
그래야만 한 화면에서 여러 채팅 메시지를 입력받고 보여줄 수 있을 테니깐요.

다음 :doc:`03-vanilla-js` 페이지에서 이를 개선해보겠습니다.
