from chatbot.models import Question

"""Admin configuration."""
from django.contrib import admin

from chatbot.models import Chatbot, Realm, Text

# Register your models here.


@admin.register(Realm)
class RealmAdmin(admin.ModelAdmin):
    """Admin for realm."""

    list_display = ['slug']


@admin.register(Chatbot)
class ChatbotAdmin(admin.ModelAdmin):
    """Admin for chatbot."""

    list_display = ['name', 'slug', 'realm']
    list_filter = ['realm']


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    """Admin for texts."""

    list_display = ['url', 'page', 'realm']
    list_filter = ['realm']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin for questions."""

    list_display = ['question', 'created_at', 'bot', 'user']
    list_filter = ['bot']
    readonly_fields = ['context', 'bot']
