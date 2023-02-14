"""Rate limiting."""

from django.conf import settings
from django.http import HttpRequest
from redis.asyncio import Redis as AsyncRedis    # pip install redis


def get_ratelimit(group: str, request: HttpRequest) -> str:
    """Rate limit for users and anon."""
    if request.user.is_authenticated:
        return settings.USER_RATE_LIMIT
    return settings.ANON_RATE_LIMIT


redis = AsyncRedis.from_url('redis://localhost:6379')
