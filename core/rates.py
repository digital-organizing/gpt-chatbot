"""Rate limiting."""
from django.conf import settings


def get_ratelimit(group, request):
    """Rate limit for users and anon."""
    if request.user.is_authenticated:
        return settings.USER_RATE_LIMIT
    return settings.ANON_RATE_LIMIT
