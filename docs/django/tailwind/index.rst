django에 tailwindcss 적용하기
========================================


tailwindcss 빠른 적용
--------------------------

초기 개발 시에는 빠르게 적용하기 위해 CDN 버전의 ``tailwindcss`` 와 ``daisyUI`` 를 사용합니다.

.. code-block:: html+django

   <link href="//cdn.jsdelivr.net/npm/daisyui@latest/dist/full.min.css" rel="stylesheet" type="text/css"/>
   <script src="//cdn.tailwindcss.com"></script>


최적화된 빌드
-----------------

``tailwindcss`` 는 nodejs 기반의 빌드 도구를 사용해서 최적화된 CSS를 생성합니다.
nodejs 없이도 사용할 수 있는 `Standalone CLI <https://tailwindcss.com/blog/standalone-cli>`_ 를 지원하지만, 기본 기능만 사용할 수 있고 확장을 위해서는 빌드 도구를 사용해야만 합니다.

장고 프로젝트 내에 직접 nodejs 프로젝트를 설정하고 ``tailwindcss`` 설정을 하실 수도 있지만,
``django-tailwind`` 라이브러리를 사용하시면 보다 수월하게 설정할 수 있습니다.


django-tailwind
---------------

`django-tailwind 설치 공식문서 <https://django-tailwind.readthedocs.io/en/latest/installation.html>`_ 를 참고해서 설치해주세요.
`nodejs 런타임도 필요하기에 OS에 맞춰 먼저 설치 <https://nodejs.org>`_ 해주셔야 합니다. 

이 앱은 장고 앱이지만 nodejs 프로젝트만 생성해주고 static 관련된 몇 가지 설정을 제공하고 npm 명령에 대한 래핑을 지원할 뿐이기에,
라이브러리 업데이트가 없더라도 최신 tailwindcss 지원도 전혀 문제가 없으니, 라이브러리의 마지막 커밋이 2년 전이지만 걱정하지 않으셔도 됩니다.

위 설치 문서를 그대로 진행하셨다면 ``theme`` 장고 앱이 생성되고, ``theme/static_src/`` 경로에 nodejs 프로젝트가 생성됩니다.
nodejs 프로젝트 이기에 그 안에서 nodejs 기반으로 다양한 ``tailwindcss`` 확장을 설치하시고 설정을 할 수 있습니다.

(중요) tailwindcss에서는 **tailwindcss 유틸리티 클래스가 사용된 디렉토리 경로를 올바르게 지정해줘야만 합니다**. 만약 ``blog/templates/blog/post_list.html`` 파일에서 tailwindcss 유틸리티 클래스를 사용하고 있더라도,
tailwindcss 빌드 프로그램이 해당 템플릿 파일을 찾지 못하면 빌드 파일에 포함되지 않습니다.
tailwindcss 설정 파일은 ``theme/static_src/tailwind.config.js`` 경로에 있습니다. 이 파일에서 ``content`` 속성에 포함된 디렉토리 경로를 올바르게 지정해줘야만 합니다.
아래 코드를 참고해서 tailwindcss를 사용하는 파일이 포함될 수 있도록 설정해주세요.

.. code-block:: js
   :caption: theme/static_src/tailwind.config.js

   /**
    * This is a minimal config.
    * For a full list of options, see https://tailwindcss.com/docs/configuration
    */

    module.exports = {
        /* tailwind css 클래스명을 사용한 소스 파일의 경로 패턴 */
        content: [
            "../../templates/**/*.html",
            "../../**/templates/**/*.html",
            "../../**/forms.py",
            "../../**/views.py",
            // "../../**/crispy_tailwind/*.py",
            // "../../**/crispy_tailwind/*.html",
            "../../**/static/**/*.js",
        ],

        /* tailwind css 플러그인 */
        plugins: [
            require("@tailwindcss/forms"),
            require("@tailwindcss/typography"),
            require("@tailwindcss/aspect-ratio"),
        ],

        /* tailwind css 테마 설정 */
        theme: {
            extend: {},
        },
    };


지원 명령
~~~~~~~~~~~

* ``python manage.py tailwind install``

  - 의존성있는 nodejs 팩키지 설치 (``npm install`` 명령)

* ``python manage.py tailwind start``

  - 개발모드로 빌드 실행하고, 변경사항을 실시간으로 감지합니다. (``npm run start`` 명령)

* ``python manage.py tailwind build``

  - 최적화된 빌드 생성 (``npm run build`` 명령)

* ``python manage.py tailwind outdated``

  - 현재 설치된 라이브러리 버전과 최신 버전을 비교합니다. (``npm outdated`` 명령)

* ``python manage.py tailwind update``

  - 라이브러리를 최신 버전으로 업데이트합니다. (``npm update`` 명령)


CSS 빌드가 생성되는 경로
~~~~~~~~~~~~~~~~~~~~~~~~

``theme/static_src/package.json`` 파일에 CSS 빌드가 생성되는 경로가 지정되어 있습니다.
``theme/static/`` 경로에 빌드된 CSS 파일이 생성됩니다.

템플릿에서 ``{% tailwindcss %}`` 태그를 사용해서 빌드된 CSS를 사용하는 HTML 태그를 자동 생성할 수 있는 데요.
상황에 따라 이 템플릿 태그를 사용하지 않고, ``theme/static/`` 경로를 참조해서 HTML 태그를 직접 작성하실 수도 있습니다.

.. code-block:: json
   :caption: theme/static_src/package.json

   {
     /* 생략 */
     "scripts": {
       "start": "npm run dev",
       "build": "npm run build:clean && npm run build:tailwind",
       "build:clean": "rimraf ../static/css/dist",
       "build:tailwind": "cross-env NODE_ENV=production tailwindcss --postcss -i ./src/styles.css -o ../static/css/dist/styles.css --minify",
       "dev": "cross-env NODE_ENV=development tailwindcss --postcss -i ./src/styles.css -o ../static/css/dist/styles.css -w",
       "tailwindcss": "node ./node_modules/tailwindcss/lib/cli.js"
     },
     /* 생략 */
    }
