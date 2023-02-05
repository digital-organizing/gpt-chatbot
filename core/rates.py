"""Rate limiting."""
from django.conf import settings
from django.http import HttpRequest


def get_ratelimit(group: str, request: HttpRequest) -> str:
    """Rate limit for users and anon."""
    if request.user.is_authenticated:
        return settings.USER_RATE_LIMIT
    return settings.ANON_RATE_LIMIT
