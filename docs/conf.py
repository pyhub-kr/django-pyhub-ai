import os
import sys
from pathlib import Path

# Add project source directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Project information
project = "django-pyhub-ai"
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
    "sphinx_togglebutton",
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

# Theme settings
# https://pydata-sphinx-theme.readthedocs.io
html_theme = "pydata_sphinx_theme"
html_favicon = "./assets/favicon-128.png"
html_context = {
    "github_user": "pyhub-kr",
    "github_repo": "django-pyhub-ai",
    "github_version": "main",
    "doc_path": "docs",
    # https://tagmanager.google.com/?hl=ko#/container/accounts/6260619830/containers/201568180/workspaces/2
    "GTM_ID": "GTM-57JDH7NG",
}
html_theme_options = {
    "use_edit_page_button": True,
    # https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/announcements.html
    "announcement": "이 라이브러리의 최신버전은 <strong>0.8.11</strong> 입니다. 버그가 수정되고, 기능이 자주 개선되고 있으니 항상 최신버전으로 사용 부탁드립니다.",
    "logo": {
        "text": "django-pyhub-ai 튜토리얼",
        "alt_text": "django-pyhub-ai 튜토리얼 - Home",
        "image_light": "./assets/favicon-128.png",
        "image_dark": "./assets/favicon-128.png",
    },
    # 상단 nav 중앙 링크
    # "external_links": [
    #     {"name": "link-one-name", "url": "https://<link-one>"},
    #     {"name": "link-two-name", "url": "https://<link-two>"}
    # ],
    "icon_links_label": "Quick Links",
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/pyhub-kr/django-pyhub-ai",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        },
        {
            "name": "Facebook 그룹",
            "url": "https://facebook.com/groups/askdjango",
            "icon": "fa-brands fa-square-facebook",
            "type": "fontawesome",
        },
        {
            "name": "유튜브 채널",
            "url": "https://www.youtube.com/@pyhub-kr",
            "icon": "fa-brands fa-youtube",
            "type": "fontawesome",
        },
        {
            "name": "인프런 장고 강의",
            "url": "https://inf.run/Fcn6n",
            "icon": "fa-solid fa-chalkboard-teacher",
            "type": "fontawesome",
        },
    ],
    # https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/navigation.html#control-how-many-navigation-levels-are-shown-by-default
    "show_nav_level": 2,
    # 지정 이름의 템플릿을 include
    # https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/layout.html#layout-footer
    # layout.html 템플릿을 재정의하여 별도 템플릿 없이 layout.html 템플릿에서 직접 footer 정의
    # "footer_start": ["copyright", "sphinx-version"],
    # "footer_end": ["theme-version"],
}

# html_show_sourcelink = False  # "view page source" 링크 제거

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
html_css_files = ["custom.css"]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "venv", ".venv"]

# suppress_warnings = [
#     'toc.excluded',
#     'myst.xref_missing',
# ]
