from langchain.globals import set_debug

from django.apps import AppConfig
from django.conf import settings


class PyhubAiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pyhub_ai"
