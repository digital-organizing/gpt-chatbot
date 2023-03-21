"""Admin configuration."""
from django.contrib import admin
from import_export import resources
from import_export.admin import ExportActionMixin

from chatbot.models import Chatbot, Question, Realm, Text

# Register your models here.


@admin.register(Realm)
class RealmAdmin(admin.ModelAdmin):
    """Admin for realm."""

    list_display = ["slug"]


@admin.register(Chatbot)
class ChatbotAdmin(admin.ModelAdmin):
    """Admin for chatbot."""

    list_display = ["name", "slug", "realm"]
    list_filter = ["realm"]


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    """Admin for texts."""

    list_display = ["url", "page", "realm"]
    list_filter = ["realm"]


class QuestionResource(resources.ModelResource):
    class Meta:
        model = Question


@admin.register(Question)
class QuestionAdmin(ExportActionMixin, admin.ModelAdmin):
    """Admin for questions."""

    resource_class = QuestionResource

    list_display = ["question", "created_at", "bot", "user", "count"]
    list_filter = ["bot"]
    readonly_fields = ["context", "bot"]

    search_fields = ["question"]
