"""Urls for the application."""

from django.urls import path
from rest_framework import routers

from chatbot.services import QuestionGlobalViewSet
from chatbot.views import (
    autocomplete_questions,
    bot_endpoint,
    bot_name,
    readme,
)

router = routers.DefaultRouter()
router.register("questions/<slug:slug>", QuestionGlobalViewSet, basename="question")

app_name = "chatbot"

urlpatterns = [
    path("bot/<slug:slug>/", bot_endpoint, name="chatbot"),
    path("bot/<slug:slug>/name/", bot_name, name="chatbot-name"),
    path("questions/", autocomplete_questions, name="question-autocomplete"),
    path("api/questions/<slug:slug>/", QuestionGlobalViewSet.as_view({"get": "list"})),
    path("", readme, name="readme"),
]
