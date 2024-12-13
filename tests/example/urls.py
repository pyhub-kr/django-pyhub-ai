from django.urls import path

from . import views
from .views import LanguageTutorChatView, TitanicDataAnalysisChatView

urlpatterns = [
    path("", views.index, name="index"),
    # chat room
    path("chat/<int:pk>/", views.chat_room, name="chat_room"),
    path("analyst/<int:pk>/", views.chat_room, name="analyst_room", kwargs={"type": "analyst"}),
    # agents
    path("agent/chat/<int:pk>/", LanguageTutorChatView.as_view(), name="language-tutor-chat"),
    path("agent/analysis/<int:pk>/", TitanicDataAnalysisChatView.as_view(), name="titanic-analysis-chat"),
]
