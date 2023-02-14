"""Urls for the application."""
from django.urls import path

from chatbot.views import (
    autocomplete_questions,
    bot_endpoint,
    bot_name,
    readme,
)

app_name = 'chatbot'

urlpatterns = [
    path('bot/<slug:slug>/', bot_endpoint, name="chatbot"),
    path('bot/<slug:slug>/name/', bot_name, name="chatbot-name"),
    path('questions/', autocomplete_questions, name="question-autocomplete"),
    path('', readme, name="readme"),
]
