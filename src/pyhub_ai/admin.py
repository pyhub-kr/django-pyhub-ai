from django.contrib import admin
from django.db.models import QuerySet

from .models import Conversation, ConversationMessage


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    pass


@admin.register(ConversationMessage)
class ConversationMessageAdmin(admin.ModelAdmin):
    list_display = ["conversation", "user", "content"]

    def get_queryset(self, request) -> QuerySet:
        qs = super().get_queryset(request)
        return qs.select_related("conversation", "user")
