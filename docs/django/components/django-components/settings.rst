==========================
django-components 설정
==========================

공식문서 : https://django-components.github.io/django-components/latest/reference/settings/

``django-components`` 버전 ``0.128`` 기준으로 작성되었습니다.


디폴트 settings
====================

.. code-block:: python

    defaults = ComponentsSettings(
        # django_components 앱이 준비된 시점에 자동으로 컴포넌트들을 검색할지 여부
        #  - 언더바(_)로 시작하는 디렉토리는 무시됩니다.
        autodiscover=True,
        # 컴포넌트의 JS/CSS 파일들을 저장할 장고 캐시명.
        #  - 디폴트로 None이며, 로컬 메모리 캐시(no timeout, no max size)가 사용됩니다.
        cache=None,

        # 컴포넌트 템플릿을 LRU 메모리에 캐시합니다.
        #  - None으로 지정하면 캐시 제한없이 모든 컴포넌트 템플릿을 캐시합니다.
        template_cache_size=128,

        # 컴포넌트 외부의 변수값들을 허용할 지 여부
        #  - "django" : 장고 템플릿 스타일과 동일하게 허용
        #  - "isolated" : 컴포넌트 내부에서만 변수값을 허용
        context_behavior=ContextBehavior.DJANGO.value,  # "django" | "isolated"

        # 루트 레벨의 컴포넌트 디렉토리 경로
        dirs=[
            Path(settings.BASE_DIR) / "components",
        ],
        # 앱 레벨에서의 컴포넌트 디렉토리 경로.
        app_dirs=[
            "components",  # `[app]/components/` 경로에서 찾습니다.
        ],

        # 여러 줄 템플릿 태그를 허용할 지 여부
        #  - 장고 템플릿 기본에서는 1줄 템플릿 태그만 허용
        multiline_tags=True,

        # 파일 변경 시 자동 리로드 여부
        reload_on_file_change=False,

        # {% component %} 템플릿 태그 사용
        tag_formatter="django_components.component_formatter",
        # {% 컴포넌트명 %} 템플릿 태그 사용
        # tag_formatter="django_components.component_shorthand_formatter",
    )
