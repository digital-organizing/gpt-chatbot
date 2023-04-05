"""Admin configuration."""
from typing import Any

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from import_export import resources

from chatbot.models import Chatbot, Question, Realm, Text


# Register your models here.
#
class RestrictedAdminMixin:
    user_relation = "users"

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(**{self.user_relation: request.user})


@admin.register(Realm)
class RealmAdmin(RestrictedAdminMixin, admin.ModelAdmin):
    """Admin for realm."""

    list_display = ["slug"]

    def get_form(self, request: Any, *args, **kwargs: Any) -> Any:
        if not request.user.is_superuser:
            self.exclude = [
                "openai_key",
                "openai_org",
            ]

        return super().get_form(request, *args, **kwargs)


@admin.register(Chatbot)
class ChatbotAdmin(RestrictedAdminMixin, admin.ModelAdmin):
    """Admin for chatbot."""

    list_display = ["name", "slug", "realm"]
    list_filter = ["realm"]

    def get_form(self, request: Any, *args, **kwargs: Any) -> Any:
        if request.user.is_superuser:
            self.exclude = []
        else:
            self.exclude = [
                "openai_key",
                "realm",
                "model",
                "model_max_tokens",
                "openai_org",
                "max_tokens",
                "users",
                "restricted",
                "slug",
                "skipt_context",
            ]

        return super().get_form(request, *args, **kwargs)


@admin.register(Text)
class TextAdmin(RestrictedAdminMixin, admin.ModelAdmin):
    """Admin for texts."""

    list_display = ["url", "page", "realm"]
    list_filter = ["realm"]
    user_relation = "realm__users"


class QuestionResource(resources.ModelResource):
    class Meta:
        model = Question


@admin.register(Question)
class QuestionAdmin(RestrictedAdminMixin, admin.ModelAdmin):
    """Admin for questions."""

    resource_class = QuestionResource

    list_display = ["question", "created_at", "bot", "user", "count"]
    list_filter = ["bot"]
    readonly_fields = ["context", "bot"]

    search_fields = ["question"]

    user_relation = "bot__users"
