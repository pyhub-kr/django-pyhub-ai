=================
장고 컴포넌트
=================


    컴포넌트는 프론트엔드 만의 전유물이 아닙니다.


UI 개발에서 매번 HTML/CSS/JavaScript를 복&붙해서 구현하기보다, 반복되는 패턴의 UI는 컴포넌트화해서 재사용하는 것이 효율적입니다.
컴포넌트 기반의 개발은 3가지 장점이 있습니다.

#. 재사용성 : 동일한 UI 요소를 여러 페이지에 걸쳐 재사용함으로써, 개발 시간이 단축되고 코드의 일관성이 유지됩니다. 이는 프로젝트 전체의 효율성을 높이는 데 기여합니다.
#. 유지보수성 : 복잡한 UI를 작은, 관리하기 쉬운 컴포넌트로 나누어 관리할 수 있습니다. 각 컴포넌트가 독립적으로 작동하므로, 한 부분을 수정하거나 업데이트할 때 다른 부분에 미치는 영향이 최소화됩니다.
#. 캡슐화 : 컴포넌트는 스타일과 기능을 내부에 캡슐화하여, 다른 코드와의 충돌 없이 독립적으로 작동합니다. 이는 컴포넌트 간의 명확한 경계를 제공하고, 전체적인 코드 구조의 견고함을 향상시킵니다.

UI 컴포넌트는 리액트나 Vue와 같은 프론트엔드 라이브러리를 통해서만 가능하다고 오해하시는 분들이 많습니다.

.. tab-set::

    .. tab-item:: 리액트 예시

        .. code-block:: jsx

            // hello_world.jsx : 컴포넌트 정의
            function HelloWorld({ name = "익명" }) {
                return <h1>Hello - {name}</h1>;
            }
            export default HelloWorld;

            // App.jsx
            import HelloWorld from "./hello_world.js";

            function App() {
                return (
                    <div>
                        <HelloWorld></HelloWorld>  /* 컴포넌트 활용 #1: 디폴트값 활용 */
                        <HelloWorld name="리액트"></HelloWorld>  /* 컴포넌트 활용 #2 */
                    </div>
                );
            }

컴포넌트가 필요해서 리액트를 썼고, 리액트를 쓰기위해 장고를 멀리하고 장고에서는 API 구현 만을 위해 썼다면,
이는 장고의 높은 생산성을 누리지 못하는 안타까운 상황입니다.

UI 컴포넌트는 리액트와 같은 프론트엔드 라이브러리에서만 구현할 수 있는 것이 아닙니다.
:doc:`django-components/index`\, :doc:`django-cotton/index` 라이브러리를 활용하여,
장고 템플릿 시스템 기반에서 컴포넌트 기반 개발을 지원할 수 있습니다.

.. tab-set::

    .. tab-item:: django-cotton 예시

        .. code-block:: html+django

            {# templates/cotton/hello_world.html : 컴포넌트 정의 #}
            <c-vars name="익명" />
            <h1>Hello - {{ name }}</h1>

            {# 컴포넌트 활용 #}
            <c-hello-world />  {# 컴포넌트 활용 #1: 디폴트값 활용 #}
            <c-hello-world name="장고" />  {# 컴포넌트 활용 #2 #}

장고 템플릿에서 UI 컴포넌트를 선언적으로 정의하고, 재사용 가능한 코드를 작성할 수 있습니다.
이는 개발 생산성을 크게 향상시키고, 코드의 유지보수성을 높이는 데 도움됩니다.
물론 리액트 기술을 얹어서, 리액트 컴포넌트를 가져와서 사용할 수도 있습니다.

----

.. toctree::
    :maxdepth: 1
    :caption: 목차

    variety
    django-components/index
