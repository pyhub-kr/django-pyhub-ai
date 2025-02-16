===========================
django-components 설치
===========================


신규로 설치한 경우
=================================

2025년 2월 기준으로 최신 버전은 ``0.128`` 입니다.

``django-components`` 라이브러리를 설치하고

.. code-block:: bash

    python -m pip install 'django-components==0.128'

``settings.INSTALLED_APPS`` 리스트에 추가합니다.

.. code-block:: python
    :caption: ``mysite/settings.py``

    INSTALLED_APPS += [
        # ...
        "django_components",
    ]

이 설정 만으로 HTML 템플릿의 컴포넌트 활용은 가능한데요.

CSS/JS 지원을 위해 추가 설정이 필요합니다.
``components/`` 폴더 안의 CSS/JS 파일을 찾기 위해, ``STATICFILES_FINDERS`` 설정에 ``ComponentsFileSystemFinder``\를 추가하구요.

.. code-block:: python
    :caption: ``mysite/settings.py``
    :emphasize-lines: 4

    STATICFILES_FINDERS = [
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
        "django_components.finders.ComponentsFileSystemFinder",
    ]

의존성있는 CSS/JS을 템플릿 단에서 자동 렌더링하기 위해 미들웨어에 ``ComponentDependencyMiddleware``\를 추가합니다.

.. code-block:: python
    :caption: ``mysite/settings.py``
    :emphasize-lines: 3

    MIDDLEWARE += [
        # ...
        "django_components.middleware.ComponentDependencyMiddleware",
    ]

자동 수집된 JS 서빙을 위해 ``mysite/urls.py`` 파일에 ``django_components.urls`` 패턴을 추가합니다.

.. code-block:: python
    :caption: ``mysite/urls.py``

    urlpatterns = [
        # ...
        path("", include("django_components.urls")),
    ]

이제 ``django-components`` 컴포넌트를 사용하는 템플릿에서는 ``<head>`` 태그에 CSS가 자동 렌더링되며, ``<body>`` 태그에 JS가 자동 렌더링됩니다.

디폴트 설정으로 ``프로젝트루트/components/`` 경로에서 컴포넌트를 찾습니다.
``프로젝트/components/`` 경로에 컴포넌트 폴더를 생성하고, 그 폴더 안에 파이썬 코드, 템플릿 코드, 정적 파일을 모두 둡니다.

.. tab-set::

    .. tab-item:: hello-world 컴포넌트 등록

        .. code-block:: python
            :caption: ``components/hello_world/hello_world.py``

            from typing import Dict

            from django_components import Component, register


            @register("hello-world")
            class HelloWorld(Component):
                template_file = "hello_world.html"
                css_file = "hello_world.css"
                js_file = "hello_world.js"

                def get_context_data(self, name=None) -> Dict:
                    return {"name": name}

    .. tab-item:: HTML 템플릿

        .. code-block:: html+django
            :caption: ``components/hello_world/hello_world.html``

            <div class="hello-world-component">
                <h1>Hello - {{ name|default:"익명" }}</h1>
            </div>

    .. tab-item:: 자바스크립트

        .. code-block:: javascript
            :caption: ``components/hello_world/hello_world.js``

            /*  - 각 컴포넌트마다 반복되는 것이 아니라, 웹페이지에서 1회만 포함됩니다. */

            (function () {
            document.querySelectorAll(".hello-world-component h1").forEach(el => {
                el.onclick = function (e) {
                alert(e.target.textContent);
                };
            });
            })()

    .. tab-item:: CSS

        .. code-block:: css
            :caption: ``components/hello_world/hello_world.css``

            /*  - 각 컴포넌트마다 반복되는 것이 아니라, 웹페이지에서 1회만 포함됩니다. */

            .hello-world-component { display: inline-block; border: 1px dashed #ccc; padding: 10px; }
            .hello-world-component h1 { cursor: pointer; color: blue; margin: 0; }
            .hello-world-component h1:hover { color: red; }


0.67 버전에서 0.128 버전으로 업그레이드할 경우
==============================================

`인프런 파이썬/장고 웹서비스 개발 완벽 가이드 with 리액트 (장고 4.2 기준) <https://inf.run/Fcn6n>`_ 강의에서는 ``django-components`` 라이브러리를 ``0.67`` 버전으로 설치했습니다.

이제 더 이상 ``django_components.safer_staticfiles`` 앱은 필요없습니다.
공식문서 `Migrating from safer_staticfiles <https://django-components.github.io/django-components/latest/migrating_from_safer_staticfiles/?h=safer_staticfiles>`_ 문서에 따르면,
``django-components`` 라이브러리 ``0.100`` 버전부터 JS/CSS 파일을 처리하는 방식이 변경되어 ``safer_staticfiles`` 앱이 제거되었다고 합니다.
강의에서 제거했던 ``django.contrib.staticfiles`` 앱을 다시 추가하고 ``django_components`` 앱만 포함해주시구요.

.. code-block:: python
    :caption: ``mysite/settings.py``

    INSTALLED_APPS = [
        # ...
        "django.contrib.staticfiles",
        "django_components",
    ]

컴포넌트 경로는 ``settings.COMPONENTS`` 설정을 통해서 지정하기에, ``TEMPLATES``, ``STATICFILES_DIRS`` 설정에 추가했던
``src-django-components`` 경로는 모두 제거합니다.

.. code-block:: python
    :emphasize-lines: 6,13
    :caption: ``mysite/settings.py``

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [
                BASE_DIR / "mysite" / "templates",
                # BASE_DIR / "components" / "src-django-components",  # 이 설정을 제거
            ],
            # 생략
        }
    ]

    STATICFILES_DIRS = [
        # BASE_DIR / "components" / "src-django-components",  # 이 설정을 제거
    ]

컴포넌트 HTML/CSS/JS 파일을 컴포넌트 디렉토리 경로에서 찾고, 렌더링할 수 있도록 아래 설정을 추가합니다.

.. code-block:: python
    :caption: ``mysite/settings.py``
    :emphasize-lines: 4,9

    STATICFILES_FINDERS = [
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
        "django_components.finders.ComponentsFileSystemFinder",
    ]

    MIDDLEWARE += [
        # ...
        "django_components.middleware.ComponentDependencyMiddleware",
    ]

자동 수집된 JS 서빙을 위해 ``mysite/urls.py`` 파일에 ``django_components.urls`` 패턴을 추가합니다.

.. code-block:: python
    :caption: ``mysite/urls.py``

    urlpatterns = [
        # ...
        path("", include("django_components.urls")),
    ]

그리고, 컴포넌트에서 템플릿 변수를 격리하는 설정이 많이 변경되었엇는 데요. 이제 ``"django"`` 값이 디폴트로서,
(``"django"``, ``"isolated"`` 중 택일)
템플릿 활용 측의 장고 템플릿 컨텍스트 변수를 사용할 수 있도록 허용합니다.
``context_behavior`` 설정을 제거하셔도 됩니다.

.. code-block:: python

    COMPONENTS = {
        "dirs": [
            # BASE_DIR / "components",  # 디폴트
            BASE_DIR / "core" / "src-django-components",
        ],
        # "context_behavior": "django",  # 디폴트 설정이므로 제거하셔도 됩니다.
    }

마지막으로 컴포넌트를 활용하는 템플릿에서는 ``{% component_js_dependencies %}`` 템플릿 태그와
``{% component_css_dependencies %}`` 템플릿 태그를 사용하지 않아도,
미들웨어에 의해서 ``<head>`` 태그에 CSS가 자동 렌더링되고, ``<body>`` 태그에 JS가 자동 렌더링됩니다.
하지만 필요한 경우 `해당 템플릿 태그를 활용하여, 렌더링 위치를 직접 지정 <https://django-components.github.io/django-components/latest/concepts/advanced/rendering_js_css/>`_\할 수 있습니다.