"""Views to access the chabot functionality."""
import os
import pathlib
from typing import Optional

import markdown
from asgiref.sync import async_to_sync, sync_to_async
from django.core.exceptions import PermissionDenied
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    JsonResponse,

)
from pygments.formatters import HtmlFormatter
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


def readme(request):
    """Render the README.MD as index view."""
    path = pathlib.Path(__file__).parent.resolve() / '../README.md'

    style = HtmlFormatter().get_style_defs('.codehilite')

    with open(path) as fp:
        content = markdown.markdown(fp.read(), extensions=['fenced_code', 'codehilite'])

    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://unpkg.com/@picocss/pico@1.*/css/pico.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Raleway:wght@300;700&display=swap" rel="stylesheet">
    <style>{style} :root {{ --font-family: 'Raleway', sans-serif; }}</style>
    <title>GPT Chatbot</title>
  </head>
  <body>
    <main class="container">
    {content}
    </main>
  </body>
</html>
    """
    return HttpResponse(html)
