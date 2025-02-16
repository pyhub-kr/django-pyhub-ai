===========================================
다양한 방법으로 만드는 장고 컴포넌트
===========================================

.. figure:: ./django-components/assets/hello-world.png


웹 컴포넌트 구현체
=====================

웹 표준에서는 `웹 컴포넌트 <https://developer.mozilla.org/ko/docs/Web/API/Web_components>`_\를 통해 재사용 가능한 커스텀 엘리먼트를 생성하고 웹 앱에서 활용할 수 있습니다.

브라우저 네이티브 지원으로 별도 라이브러리없이 특정 프레임워크에 종속되지 않은 컴포넌트를 개발할 수 있으며
표준 기술이므로 장기적인 호환성도 보장됩니다.

`Shadow DOM <https://developer.mozilla.org/ko/docs/Web/API/Web_components/Using_shadow_DOM>`_\을 통하여 호스트 요소와 격리된 컴포넌트를 생성할 수 있습니다. 이는 컴포넌트의 스타일과 동작을 완벽하게 캡슐화할 수 있다는 장점이 있지만, 동시에 외부에서 스타일을 적용하거나 컴포넌트와 상호작용하기 어렵게 만드는 단점이 될 수도 있습니다.

* 실행 예시 : https://codepen.io/Chinseok-Lee/pen/zxYGVyG

.. tab-set::

    .. tab-item:: html

        .. code-block:: html+django

            <script src="./hello-world.js"></script>

            <hello-world name="장고"></hello-world>
            <hello-world name="익명"></hello-world>

    .. tab-item:: hello-world.js

        .. code-block:: javascript

            class HelloWorld extends HTMLElement {
                constructor() {
                    super();
                    this.attachShadow({ mode: 'open' });
                }

                async connectedCallback() {
                    const name = this.getAttribute('name') || '익명';

                    // 외부 CSS 파일을 로드하여 Shadow DOM에 추가
                    const link = document.createElement('link');
                    link.rel = 'stylesheet';
                    link.href = 'hello-world.css';

                    // h1 요소 생성 및 이벤트 리스너 추가
                    const h1 = document.createElement('h1');
                    h1.textContent = `Hello - ${name}`;
                    h1.addEventListener('click', () => {
                        alert(h1.textContent);
                    });

                    // Shadow DOM에 요소 추가
                    this.shadowRoot.append(link, h1);
                }
            }

            customElements.define('hello-world', HelloWorld);

    .. tab-item:: hello-world.css

        .. code-block:: css

            :host {
                display: inline-block;
                border: 1px dashed #ccc;
                padding: 10px;
            }

            h1 {
                cursor: pointer;
                color: blue;
                margin: 0;
            }

            h1:hover {
                color: red;
            }


.. admonition:: MDN 웹 컴포넌트 예제
    :class: tip

    https://github.com/mdn/web-components-examples


장고 기본 템플릿 엔진으로 만든 컴포넌트
==========================================

예시
----------

이번에는 장고 템플릿 시스템을 활용하여 ``components-pure/hello-world.html`` 경로에 컴포넌트를 만들어두면,
모든 장고 템플릿 영역에서 ``include`` 템플릿 태그를 통해 ``hello-world`` 템플릿을 가져와서 렌더링할 수 있습니다.
프론트엔드 개발자가 컴포넌트를 개발하면, 백엔드 개발자는 프론트엔드에 대한 깊은 이해 없이도 
``include`` 태그만으로 **HTML 코드 중복을 막고 재사용성을 높일 수 있습니다**\.
추가로 필요한 context data가 있다면 ``with``\를 통해 값을 전달합니다.

.. code-block:: html+django

    {% include "components-pure/hello-world.html" with name="파이썬" %}
    {% include "components-pure/hello-world.html" %}

.. tab-set::

    .. tab-item:: hello-world.html

        .. code-block:: html+django
            :caption: ``templates/components-pure/hello-world.html``

            {% load static %}

            <link rel="stylesheet" href="{% static 'components-pure/hello-world.css' %}" />
            <div class="hello-world-component">
                <h1>Hello - {{ name|default:"익명" }}</h1>
            </div>
            <script src="{% static 'components-pure/hello-world.js' %}"></script>

    .. tab-item:: hello-world.css

        .. code-block:: css

            /* static/components-pure/hello-world.css */

            .hello-world-component { display: inline-block; border: 1px dashed #ccc; padding: 10px; }
            .hello-world-component h1 { cursor: pointer; color: blue; margin: 0; }
            .hello-world-component h1:hover { color: red; }

    .. tab-item:: hello-world.js

        .. code-block:: javascript

            /* static/components-pure/hello-world.js */

            (function () {
                document.querySelectorAll(".hello-world-component h1").forEach(el => {
                    el.onclick = function (e) {
                        alert(e.target.textContent);
                    };
                });
            })()


CSS는 전역 스코프를 가지기 때문에, 다른 컴포넌트나 페이지의 스타일과 충돌할 수 있습니다. 이를 방지하기 위해서
컴포넌트 별로 고유한 클래스명 사용하여 스타일 충돌을 방지할 수 있습니다. 자바스크립트에서도 동일한 클래스명으로 요소를 선택하여 이벤트를 처리합니다.

컴포넌트를 사용한 횟수 만큼 HTML에 같은 JS/CSS 선언이 중복으로 추가되지만, 같은 URL 경로의 파일이기에 브라우저에서는 브라우저 캐시를 활용하여 중복 요청을 하지 않습니다.


제약사항
-------------

장고 템플릿을 활용한 컴포넌트 방식은 컴포넌트 속성값을 정의할 때 가독성이 떨어집니다. 여러 속성을 전달하고자 할 때, 모든 속성을 ``with`` 구문 뒤에 나열해야 합니다.

.. code-block:: html+django

    {% include "user-profile.html" with name="홍길동" age=20 email="hong@example.com" role="admin" is_active=True avatar_url="/static/images/default.png" %}

장고 템플릿 태그는 한 줄에 작성해야 하는 제약이 있어, 많은 속성을 가진 컴포넌트의 경우 코드의 가독성이 크게 저하됩니다. 위 예시처럼 긴 줄의 코드는 유지보수가 어렵고 실수하기 쉽습니다.

.. admonition:: 템플릿 태그를 여러 줄로 쓰면 템플릿 태그가 아닌 문자열로 처리됩니다.
    :class: warning

    아래와 같이 하나의 템플릿 태그를 여러 줄로 나눠쓰면, 템플릿 태그가 아닌 문자열로 처리되어 유저에게 코드 그대로 노출되거나
    ``TemplateSyntaxError`` 예외가 발생합니다.

    .. code-block:: html+django

        {% include "user-profile.html"
           with name="홍길동" age=20 %}

.. tip::

    ``django-components`` 라이브러리에서는 ``settings.COMPONENTS.multiline_tag = True`` 설정 (디폴트)을 통해
    `여러 줄의 템플릿 태그를 지원 <https://django-components.github.io/django-components/latest/concepts/fundamentals/template_tag_syntax/?h=multiline#multiline-tags>`_\합니다.


또한 컴포넌트에 기본값을 설정하거나 속성값의 유효성을 검사하는 등의 로직을 구현하기가 번거롭습니다. 이러한 로직은 템플릿 내에서 처리해야 하므로, 코드가 복잡해지고 유지보수가 어려워질 수 있습니다.

이러한 방식의 컴포넌트는 단순한 템플릿 코드 재사용 목적으로만 유용합니다. 컴포넌트 간의 상호작용이나 상태 관리, 이벤트 처리 등 복잡한 기능을 구현하기에는 한계가 있습니다.


아이콘 컴포넌트
-------------------

SVG 아이콘은 xml 형식으로 작성됩니다. SVG 아이콘을 static 파일로서 저장하게 되면 저장된 스타일로만 아이콘을 사용할 수 있을 뿐 커스터마이징을 할 수 없습니다.
아래와 같은 아이콘이 필요하면 매번 SVG 코드를 복사해서 별도 파일로서 미리 생성을 해줘야 합니다.

.. raw:: html

    <svg viewBox="0 0 512 512" width="128" height="128">
        <g fill="none" stroke-width="30" stroke-linejoin="round"
           stroke="#000"
        >
            <path d="M143.533 256 79.267 384.533v-192.8L497 127.467z"/>
            <path d="M143.533 256 79.267 384.533l119.352-73.448zM15 127.467h482L79.267 191.733z"/>
            <path d="M143.533 256 497 127.467l-241 241z"/>
        </g>
    </svg>

    <svg viewBox="0 0 512 512" width="128" height="128">
        <g fill="none" stroke-width="30" stroke-linejoin="round"
           stroke="#FF6666"
        >
            <path d="M143.533 256 79.267 384.533v-192.8L497 127.467z"/>
            <path d="M143.533 256 79.267 384.533l119.352-73.448zM15 127.467h482L79.267 191.733z"/>
            <path d="M143.533 256 497 127.467l-241 241z"/>
        </g>
    </svg>

    <svg viewBox="0 0 512 512" width="128" height="128">
        <g fill="none" stroke-width="30" stroke-linejoin="round"
           stroke="#3399FF"
        >
            <path d="M143.533 256 79.267 384.533v-192.8L497 127.467z"/>
            <path d="M143.533 256 79.267 384.533l119.352-73.448zM15 127.467h482L79.267 191.733z"/>
            <path d="M143.533 256 497 127.467l-241 241z"/>
        </g>
    </svg>

    <svg viewBox="0 0 512 512" width="128" height="128">
        <g fill="none" stroke-width="30" stroke-linejoin="round"
           stroke="#9933FF"
        >
            <path d="M143.533 256 79.267 384.533v-192.8L497 127.467z"/>
            <path d="M143.533 256 79.267 384.533l119.352-73.448zM15 127.467h482L79.267 191.733z"/>
            <path d="M143.533 256 497 127.467l-241 241z"/>
        </g>
    </svg>

SVG 아이콘은 xml 코드니깐요. 장고 템플릿을 통해 컴포넌트화를 시키면 

.. code-block:: html+django
    :emphasize-lines: 3
    :caption: ``templates/icons/plane.html``

    <svg viewBox="0 0 512 512" width="128" height="128">
        <g fill="none" stroke-width="30" stroke-linejoin="round"
           stroke="{{ color }}"
        >
            <path d="M143.533 256 79.267 384.533v-192.8L497 127.467z"/>
            <path d="M143.533 256 79.267 384.533l119.352-73.448zM15 127.467h482L79.267 191.733z"/>
            <path d="M143.533 256 497 127.467l-241 241z"/>
        </g>
    </svg>

언제든 원하는 옵션으로 SVG 아이콘을 생성해서 사용하실 수 있게 됩니다.

.. code-block:: html+django

    {% include "icons/plane.html" with color="#000" %}
    {% include "icons/plane.html" with color="#FF6666" %}
    {% include "icons/plane.html" with color="#3399FF" %}
    {% include "icons/plane.html" with color="#9933FF" %}


django-cotton 라이브러리로 만든 컴포넌트
===============================================

아이콘 컴포넌트
-----------------

위에서 살펴본 아이콘 컴포넌트는 ``django-cotton`` 라이브러리를 활용하시면,
`컴포넌트를 사용하는 코드를 더 간결하게 <https://django-cotton.com/docs/icons>`_ 사용하실 수 있습니다.
장고 템플릿 시스템을 활용하지만 좀 더 프론트엔드 개발자들이 좋아하는 방식의 코드입니다. 😉

.. code-block:: html+django

    <c-icons.plane color="#000" />
    <c-icons.plane color="#FF6666" />
    <c-icons.plane color="#3399FF" />
    <c-icons.plane color="#9933FF" />

``django-cotton`` 활용을 위해서 템플릿 파일만 ``cotton`` 디렉토리 경로에 생성하시면,
``include`` 템플릿 태그 없이도 ``c-`` 클래스 이름을 통해 컴포넌트를 사용할 수 있습니다.

.. code-block:: html+django
    :emphasize-lines: 3
    :caption: ``templates/cotton/icons/plane.html``

    <svg viewBox="0 0 512 512" width="128" height="128">
        <g fill="none" stroke-width="30" stroke-linejoin="round"
           stroke="{{ color }}"
        >
            <path d="M143.533 256 79.267 384.533v-192.8L497 127.467z"/>
            <path d="M143.533 256 79.267 384.533l119.352-73.448zM15 127.467h482L79.267 191.733z"/>
            <path d="M143.533 256 497 127.467l-241 241z"/>
        </g>
    </svg>


c-hello-world 컴포넌트
--------------------------

위에서 살펴본 ``hello-world`` 컴포넌트를 ``django-cotton`` 라이브러리를 활용하여 만들어보겠습니다.
css/js 파일도 cotton 경로에 맞춰 생성했습니다.

.. tab-set::

    .. tab-item:: hello-world.html

        .. code-block:: html+django
            :emphasize-lines: 1-2,8

            {# templates/cotton/hello-world.html #}
            <c-vars name="익명" />

            {% load static %}

            <link rel="stylesheet" href="{% static 'cotton/hello-world.css' %}" />
            <div class="hello-world-component">
                <h1>Hello - {{ name }}</h1>
            </div>
            <script src="{% static 'cotton/hello-world.js' %}"></script>

    .. tab-item:: hello-world.css

        .. code-block:: css
            :emphasize-lines: 1

            /* static/cotton/hello-world.css */

            .hello-world-component { display: inline-block; border: 1px dashed #ccc; padding: 10px; }
            .hello-world-component h1 { cursor: pointer; color: blue; margin: 0; }
            .hello-world-component h1:hover { color: red; }

    .. tab-item:: hello-world.js

        .. code-block:: javascript
            :emphasize-lines: 1

            /* static/cotton/hello-world.js */

            (function () {
              document.querySelectorAll(".hello-world-component h1").forEach(el => {
                el.onclick = function (e) {
                  alert(e.target.textContent);
                };
              });
            })()

``cotton`` 디렉토리 아래에 ``hello_world.html`` 템플릿 파일이 있으므로,
``c-hello-world`` 클래스 이름을 통해 컴포넌트를 사용할 수 있습니다.

.. code-block:: html+django

    <c-hello-world name="파이썬"></c-hello-world>
    <c-hello-world></c-hello-world>


django-components 라이브러리로 만든 컴포넌트
=========================================================

TODO: 예제 추가

.. code-block:: html+django

    {% component "hello-world" name="파이썬" %}{% endcomponent %}
    {% component "hello-world" %}{% endcomponent %}
