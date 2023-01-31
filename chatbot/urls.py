"""Urls for the application."""
from django.urls import path

from chatbot.views import bot_endpoint, readme

app_name = 'chatbot'

urlpatterns = [
    path('bot/<slug:slug>/', bot_endpoint, name="chatbot"),
    path('', readme, name="readme"),
]
