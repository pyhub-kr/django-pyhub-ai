# Generated by Django 4.2.16 on 2024-12-20 07:11

import django.db.models.deletion
import django_lifecycle.mixins
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("pyhub_ai", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ChatRoom",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "language",
                    models.CharField(
                        choices=[
                            ("English", "영어"),
                            ("Korean", "한국어"),
                            ("Chinese", "중국어"),
                            ("Japanese", "일본어"),
                            ("Spanish", "스페인어"),
                            ("French", "프랑스어"),
                            ("German", "독일어"),
                            ("Italian", "이탈리아어"),
                            ("Portuguese", "포르투갈어"),
                            ("Russian", "러시아어"),
                            ("Arabic", "아랍어"),
                            ("Hindi", "힌디어"),
                            ("Vietnamese", "베트남어"),
                            ("Thai", "태국어"),
                            ("Indonesian", "인도네시아어"),
                            ("Turkish", "터키어"),
                        ],
                        default="English",
                        max_length=20,
                        verbose_name="언어",
                    ),
                ),
                ("situation", models.TextField(default="친구와 식당에서 식사하는 상황", verbose_name="상황")),
                (
                    "level",
                    models.CharField(
                        choices=[("beginner", "초급"), ("intermediate", "중급"), ("advanced", "고급")],
                        default="beginner",
                        max_length=20,
                        verbose_name="레벨",
                    ),
                ),
                (
                    "conversation",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.SET_NULL, to="pyhub_ai.conversation"
                    ),
                ),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "abstract": False,
            },
            bases=(django_lifecycle.mixins.LifecycleModelMixin, models.Model),
        ),
    ]