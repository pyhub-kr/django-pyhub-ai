import os
import sys
from datetime import date
from pathlib import Path

import django
from django.conf import settings

# Add project source directory to Python path
sys.path.insert(0, str((Path(__file__).parent.parent / "src").resolve()))

# 문서 내에서 장고 코드 로딩을 위한 장고 프로젝트 로딩
settings.configure(
    INSTALLED_APPS=[
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "pyhub_ai",
    ],
)
django.setup()

# Project information
project = "django-pyhub-ai"
copyright = f"{date.today().year}, 파이썬사랑방"
author = "Chinseok Lee"

# Extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_sitemap",
    "sphinx_togglebutton",
    "sphinxcontrib.mermaid",
    "sphinx_gitstamp",
    "sphinxext.opengraph",
    "notfound.extension",
    "myst_parser",
]

myst_enable_extensions = ["colon_fence"]

# https://sphinx-design.readthedocs.io/en/pydata-theme/get_started.html#creating-custom-directives
sd_custom_directives = {
    "dropdown-syntax": {
        "inherit": "dropdown",
        "argument": "Syntax",
        "options": {
            "color": "primary",
            "icon": "code",
        },
    }
}

is_enable_comments = True

if is_enable_comments:
    extensions.append("sphinx_comments")
    # https://sphinx-comments.readthedocs.io/en/latest/utterances.html#activate-utteranc-es
    comments_config = {
        "utterances": {
            "repo": "pyhub-kr/django-pyhub-ai-feedback",
            "issue-term": "pathname",
            "theme": "github-light",
            "label": "comment",
            "crossorigin": "anonymous",
        }
    }

# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-language
language = "ko"

# Theme settings
# https://pydata-sphinx-theme.readthedocs.io
html_theme = "furo"
# https://pradyunsg.me/furo/customisation/sidebar-title/
html_title = "파이썬사랑방 튜토리얼"
html_favicon = "./assets/favicon-128.png"
html_context = {
    "github_user": "pyhub-kr",
    "github_repo": "django-pyhub-ai",
    "github_version": "main",
    "doc_path": "docs",
    # https://tagmanager.google.com/?hl=ko#/container/accounts/6260619830/containers/201568180/workspaces/2
    "GTM_CONTAINER_ID": os.environ.get("GTM_CONTAINER_ID"),  # , "GTM-57JDH7NG"),
    "GA4_TRACKING_ID": os.environ.get("GA4_TRACKING_ID"),  # , "G-RJ6B2YKGQ2"),
    "REDIRECT_HOST": os.environ.get("REDIRECT_HOST"),
}
html_theme_options = {
    "source_edit_link": None,
    # https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/announcements.html
    # "announcement": "django-pyhub-ai 라이브러리의 최신버전은 <em>0.8.25</em> 입니다. 버그가 수정되고, 기능이 자주 개선되고 있으니 항상 최신버전으로 사용 부탁드립니다.",
    # "announcement": "야심차게 준비한 <a href='/rag-01/'>RAG 초보자 튜토리얼</a>을 공개합니다. 많은 관심과 널리 공유 부탁드립니다. 🥳",
    # "announcement": "2025.2.1. (토) 오후 9시에 <a href='https://youtube.com/live/Lzy9F_Hv4z8' target='_blank'>튜토리얼 따라하기 세번째 라이브</a>를 진행합니다. 함께 해요. ;-)",
    "announcement": "첫번째 RAG 튜토리얼 라이브를 마무리했습니다. 곧 두번째 RAG 튜토리얼도 오픈합니다. 많은 관심 부탁드립니다. 🥳",
    "light_logo": "favicon-128.png",  # _static 경로
    "dark_logo": "favicon-128.png",
    # https://pradyunsg.me/furo/customisation/colors/
    "light_css_variables": {
        # "color-brand-primary": "#216DB2",
        # "color-brand-content": "#216DB2",
        "font-stack--monospace": "Ubuntu Mono",
        # "font-size--normal": "100%",  # default: 100%
        "font-size--small": "95%",  # default: 87.5%
        "font-size--small--2": "87.5%",  # default: 81.25%
        "font-size--small--3": "81.25%",  # default: 75%
        "font-size--small--4": "75%",  # 62.5%
        # "code-font-size": "100%",
    },
    # https://pradyunsg.me/furo/customisation/top-of-page-buttons/#with-popular-vcs-hosts
    "source_repository": "https://github.com/pyhub-kr/django-pyhub-ai",
    "source_branch": "main",
    "source_directory": "docs/",
    # https://pradyunsg.me/furo/customisation/footer/
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/pyhub-kr/django-pyhub-ai",
            # 커스텀 css 적용을 위해 HTML 사용
            "html": """
                <span class='fa-brands fa-github fa-solid' style='margin-right: 0.5rem;'
                      title='GitHub 저장소'></span>
            """,
            # "class": "fa-brands fa-github fa-solid fa-2x",
        },
        {
            "name": "Facebook 그룹",
            "url": "https://facebook.com/groups/askdjango",
            "html": """
                <span class='fa-brands fa-facebook fa-solid' style='margin-right: 0.5rem;'
                      title='Facebook 그룹'></span>
            """,
        },
        {
            "name": "유튜브 채널",
            "url": "https://www.youtube.com/@pyhub-kr",
            "html": """
                <span class='fa-brands fa-youtube fa-solid' style='margin-right: 0.5rem;'
                      title='유튜브 채널'></span>
            """,
        },
        {
            "name": "인프런 장고 강의",
            "url": "https://inf.run/Fcn6n",
            "html": """
                <span class='fa-chalkboard-teacher fa-solid' style='margin-right: 0.5rem;'
                      title='인프런 장고 강의'></span>
            """,
        },
    ],
    # 지정 이름의 템플릿을 include
    # https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/layout.html#layout-footer
    # layout.html 템플릿을 재정의하여 별도 템플릿 없이 layout.html 템플릿에서 직접 footer 정의
    # "footer_start": ["copyright", "sphinx-version"],
    # "footer_end": ["theme-version"],
}

html_show_sourcelink = False  # "view page source" 링크 제거
html_copy_source = False  # "Copy source" 링크 제거

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": ("https://docs.djangoproject.com/en/stable/", "https://docs.djangoproject.com/en/stable/_objects/"),
}

# The master toctree document
master_doc = "index"

# Markdown support
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

templates_path = ["_templates", "templates"]

html_static_path = ["_static"]
html_css_files = [
    "custom.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/fontawesome.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/solid.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/brands.min.css",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "venv", ".venv"]

# suppress_warnings = [
#     'toc.excluded',
#     'myst.xref_missing',
# ]

# furo 설정
# https://pradyunsg.me/furo/customisation/colors/#code-block-styling
# pygments_style = "sphinx"
# pygments_dark_style = "inkpot"

# -- Options for autodoc ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

# Automatically extract typehints when specified and place them in
# descriptions of the relevant function/method.
autodoc_typehints = "description"

# Don't show class signature with the class' name.
autodoc_class_signature = "separated"

# https://github.com/mgaitan/sphinxcontrib-mermaid?tab=readme-ov-file#config-values
# mermaid_output_format = "svg"  # mmdc 명령어가 필요


# https://www.sphinx-doc.org/en/master/development/tutorials/extending_build.html
todo_include_todos = True


# sphinx-sitemap : https://sphinx-sitemap.readthedocs.io/en/latest/getting-started.html
html_baseurl = "https://ai.pyhub.kr"
# sitemap_filename = "sitemap.xml"
sitemap_excludes = [
    "search.html",
    "genindex.html",
]


# https://github.com/jdillard/sphinx-gitstamp
gitstamp_fmt = "%Y-%m-%d %H:%M %z"


# https://sphinxext-opengraph.readthedocs.io/en/latest/
ogp_site_url = "https://ai.pyhub.kr"
ogp_type = "article"
ogp_custom_meta_tags = [
    #  og:url 대신 해당 페이지의 URL을 직접 사용하도록 설정
    '<meta property="og:ignore_canonical" content="true" />',
]
ogp_enable_meta_description = True
# https://sphinxext-opengraph.readthedocs.io/en/latest/socialcards.html
ogp_social_cards = {
    "enable": False,
}
