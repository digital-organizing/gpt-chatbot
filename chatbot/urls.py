"""Urls for the application."""
from django.urls import path

from chatbot.views import bot_endpoint

app_name = 'chatbot'

urlpatterns = [
    path('bot/<slug:slug>/', bot_endpoint, name="chatbot"),
]
