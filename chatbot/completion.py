"""Completion engine."""
from typing import cast

import backoff
import openai
import openai.error
from asyncio_redis_rate_limit import RateLimiter, RateLimitError, RateSpec
from redis.asyncio import Redis as AsyncRedis

from chatbot.models import Chatbot
from usage.services import astore_charge


@backoff.on_exception(
    backoff.constant,
    (RateLimitError, openai.error.RateLimitError, openai.error.TryAgain),
    max_time=60,
    interval=8,
)
async def generate_completion(
    prompt: str, context: str, question: str, chatbot: Chatbot
) -> str:
    """Generate completion using the prompt and settings from the chatbot."""
    redis = AsyncRedis.from_url("redis://redis:6379")
    async with RateLimiter(
        unique_key="openai_completion",
        rate_spec=RateSpec(requests=60, seconds=60),
        backend=redis,
        cache_prefix="openai_completion",
    ):
        response = await openai.ChatCompletion.acreate(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "system", "content": context},
                {"role": "user", "content": question},
            ],
            api_key=chatbot.openai_key,
            model=chatbot.model,
            max_tokens=chatbot.max_tokens,
            temperature=chatbot.temperature,
            presence_penalty=chatbot.presence_penality,
            frequency_penalty=chatbot.frequency_penality,
            user=chatbot.slug,
        )

    await astore_charge(chatbot.openai_org, response)

    return cast(str, response["choices"][0]["message"]["content"])
