"""Views to access the chabot functionality."""
from typing import Optional

from asgiref.sync import async_to_sync, sync_to_async
from django.core.exceptions import PermissionDenied
from django.http import (
    Http404,
    HttpRequest,
    HttpResponseBadRequest,
    JsonResponse,
)
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit

from chatbot.completion import generate_completion
from chatbot.models import Chatbot
from chatbot.services import find_texts, generate_prompt, store_question
from core import rates


@sync_to_async
@ratelimit(key='user_or_ip', rate=rates.get_ratelimit)
@cache_page(60 * 10)
@csrf_exempt
@async_to_sync
async def bot_endpoint(request: HttpRequest, slug: str):
    """View to ask questions."""
    chatbot: Optional[Chatbot] = await Chatbot.objects.filter(slug=slug).afirst()

    if chatbot is None:
        raise Http404("Chatbot not found")

    if not chatbot.public:
        if sync_to_async(lambda: request.user.is_anonymous)():
            raise PermissionDenied("You need to log in to use this bot.")

        if sync_to_async(lambda chatbot: request.user not in chatbot.users.all())(chatbot):
            raise PermissionDenied("You are not allowed to use this bot.")

    question = request.GET.get('question', None)

    if question is None:
        return HttpResponseBadRequest("You need to provide a question.")
    texts = await find_texts(question, await sync_to_async(lambda chatbot: chatbot.realm)(chatbot))

    prompt = generate_prompt(question, texts, chatbot)

    answer = await generate_completion(prompt, chatbot)

    await store_question(question, answer, prompt, texts, chatbot)

    text_list = [{
        'id': text.id,
        'content': text.content,
        'url': text.url,
        'page': text.page,
    } for text in texts if not text.internal]

    return JsonResponse({
        'answer': answer,
        'texts': text_list,
    })
