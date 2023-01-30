"""Views to access the chabot functionality."""
import json

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit

from chatbot.models import Chatbot
from chatbot.services import find_texts, generate_answer, store_question
from core import rates

# Create your views here.


@ratelimit(key='user_or_ip', rate=rates.get_ratelimit)
@cache_page(60 * 10)
@csrf_exempt
def bot_endpoint(request: HttpRequest, slug: str):
    """View to ask questions."""
    chatbot: Chatbot = get_object_or_404(Chatbot, slug=slug)

    if not chatbot.public:
        if request.user.is_anonymous:
            raise PermissionDenied("You need to log in to use this bot.")

        if request.user not in chatbot.users.all():
            raise PermissionDenied("You are not allowed to use this bot.")

    question = request.GET.get('question', None)

    if question is None:
        return HttpResponseBadRequest("You need to provide a question.")

    texts = find_texts(question, chatbot.realm)

    answer = generate_answer(question, texts, chatbot)

    store_question(question, answer, texts, chatbot)

    return JsonResponse({
        'answer': answer,
        'texts': list(texts.filter(internal=False).values('id', 'content', 'url', 'page')),
    })
