from django.conf import settings
from django.db import models
from django_lifecycle import AFTER_UPDATE, LifecycleModel, hook

from pyhub_ai.models import Conversation


class ChatRoom(LifecycleModel):
    class Language(models.TextChoices):
        ENGLISH = "English", "영어"
        KOREAN = "Korean", "한국어"
        CHINESE = "Chinese", "중국어"
        JAPANESE = "Japanese", "일본어"
        SPANISH = "Spanish", "스페인어"
        FRENCH = "French", "프랑스어"
        GERMAN = "German", "독일어"
        ITALIAN = "Italian", "이탈리아어"
        PORTUGUESE = "Portuguese", "포르투갈어"
        RUSSIAN = "Russian", "러시아어"
        ARABIC = "Arabic", "아랍어"
        HINDI = "Hindi", "힌디어"
        VIETNAMESE = "Vietnamese", "베트남어"
        THAI = "Thai", "태국어"
        INDONESIAN = "Indonesian", "인도네시아어"
        TURKISH = "Turkish", "터키어"

    class Level(models.TextChoices):
        BEGINNER = "beginner", "초급"
        INTERMEDIATE = "intermediate", "중급"
        ADVANCED = "advanced", "고급"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.SET_NULL,
        null=True,
    )
    language = models.CharField(
        max_length=20,
        choices=Language.choices,
        default=Language.ENGLISH,
        verbose_name="언어",
    )
    situation = models.TextField(verbose_name="상황", default="친구와 식당에서 식사하는 상황")
    level = models.CharField(
        max_length=20,
        choices=Level.choices,
        default=Level.BEGINNER,
        verbose_name="레벨",
    )

    @hook(AFTER_UPDATE)
    def on_after_update(self):
        """ChatRoom 설정이 변경되면, 대화 목록을 제거합니다."""
        if self.conversation:
            self.conversation.conversationmessage_set.all().delete()
