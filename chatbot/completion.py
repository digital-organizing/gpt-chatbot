"""Completion engine."""
from typing import cast

import openai

from chatbot.models import Chatbot
from usage.services import astore_charge


async def generate_completion(prompt: str, chatbot: Chatbot) -> str:
    """Generate completion using the prompt and settings from the chatbot."""
    response = await openai.Completion.acreate(
        prompt=prompt,
        api_key=chatbot.openai_key,
        model=chatbot.model,
        max_tokens=chatbot.max_tokens,
        temperature=chatbot.temperature,
        presence_penalty=chatbot.presence_penality,
        frequency_penalty=chatbot.frequency_penality,
        user=chatbot.slug,
    )

    await astore_charge(chatbot.openai_org, response)

    return cast(str, response['choices'][0]['text'])
