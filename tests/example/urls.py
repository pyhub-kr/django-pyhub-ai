from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # chat room
    path("chat/", views.chat_room, name="chat_room"),
    path("analysis/", views.chat_room, name="analysis_room", kwargs={"type": "analysis"}),
]
