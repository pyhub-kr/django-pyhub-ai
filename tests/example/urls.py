from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("chat/<int:pk>/", views.chat, name="chat"),
]
