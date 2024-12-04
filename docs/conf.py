import os
import sys
from pathlib import Path

# Add project source directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Project information
project = "django-pyhub-ai"
copyright = "2024, 파이썬사랑방"
author = "Chinseok Lee"

# Extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_comments",
    "sphinx_rtd_theme",
    "myst_parser",
]

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
html_show_sourcelink = False  # "view page source" 링크 제거

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": ("https://docs.djangoproject.com/en/stable/", "https://docs.djangoproject.com/en/stable/_objects/"),
}

# The master toctree document
master_doc = "index"

# Markdown support
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
} 

# templates_path = ["_templates"]
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'venv', ".venv"]

# suppress_warnings = [
#     'toc.excluded',
#     'myst.xref_missing',
# ]

