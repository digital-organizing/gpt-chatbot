"""Functions implementing the functionality of the chatbots."""
from typing import List, Optional, Tuple

import openai
from asgiref.sync import sync_to_async
from django_filters import filters
from rest_framework import viewsets
from rest_framework_datatables.django_filters.backends import (
    DatatablesFilterBackend,
)
from rest_framework_datatables.django_filters.filters import GlobalFilter
from rest_framework_datatables.django_filters.filterset import (
    DatatablesFilterSet,
)
from tqdm import tqdm

from chatbot.collections import (
    build_index,
    collection_exists,
    create_collection,
    drop_collection,
    insert_embeddings_into,
    search_in_collection,
)
from chatbot.embeddings import batch_embedding, count_tokens, single_embedding
from chatbot.models import Chatbot, Question, Realm, Text
from chatbot.serializers import QuestionSerializer


def get_distance(entry: Tuple[float, Text]) -> float:
    return entry[0]


async def find_question(question: str, bot: Chatbot) -> Optional[Question]:
    query = await Question.objects.filter(question__iexact=question, bot=bot).afirst()

    return query


async def similair_questions(question: str):
    query = (
        Question.objects.all()
        .filter(question__search=question, approved=True)
        .distinct("question")
        .values_list(
            "question",
            flat=True,
        )[:10]
    )

    return [question async for question in query]


async def is_input_flagged(text: str, bot: Chatbot) -> bool:
    if not bot.restricted:
        return False

    response = await openai.Moderation.acreate(
        input=text,
        api_key=bot.openai_key,
    )
    return response["results"][0]["flagged"]


async def find_texts(question: str, realm: Realm) -> List[Text]:
    """Find texts realted to the question."""
    question_embedding = await single_embedding(
        question,
        realm.openai_key,
        realm.embedding_model,
        realm.slug,
        realm.openai_org,
    )

    result = search_in_collection(question_embedding, realm.slug, n=20)

    text_ids = result.ids
    distances = result.distances

    texts: List[Text] = await sync_to_async(
        lambda: [
            text
            for _, text in sorted(
                zip(
                    distances,
                    Text.objects.filter(id__in=text_ids),
                ),
                key=get_distance,
            )
        ]
    )()

    return texts


def _format_context(texts: List[Text], max_tokens: int) -> str:
    result = ""

    for text in texts:
        context = f"[{text.id}] {text.content}\n"

        if count_tokens(result + context) > max_tokens:
            return result

        result += context

    return result


def generate_prompt_context(question: str, texts: List[Text], chatbot: Chatbot) -> str:
    """Generate an answer to the question using the texts and the configuration of the chatbot."""
    prompt_length = count_tokens(chatbot.prompt_template) + count_tokens(question)

    return _format_context(
        texts, chatbot.model_max_tokens - prompt_length - chatbot.max_tokens
    )


def index_realm(slug: str, batch_size: int = 10_000, monitor: bool = False) -> None:
    """Create embedding for each text in the realm and add it to the milvus index."""
    realm = Realm.objects.get(slug=slug)

    texts = Text.objects.filter(realm=realm, indexed=False)

    if not collection_exists(realm.slug):
        create_collection(realm.slug, realm.embedding_dim)

    ids, contents = [], []

    for text in tqdm(texts.iterator(), total=texts.count()):
        ids.append(text.pk)
        contents.append(text.content)
        if len(ids) < batch_size:
            continue
        if monitor:
            print(contents[-1])
        embeddings = batch_embedding(
            contents,
            realm.openai_key,
            realm.embedding_model,
            realm.slug,
            realm.openai_org,
        )
        insert_embeddings_into(ids, embeddings, realm.slug)
        Text.objects.filter(id__in=ids).update(indexed=True)
        ids, contents = [], []

    if len(ids) > 0:
        embeddings = batch_embedding(
            contents,
            realm.openai_key,
            realm.embedding_model,
            realm.slug,
            realm.openai_org,
        )
        insert_embeddings_into(ids, embeddings, realm.slug)
        Text.objects.filter(id__in=ids).update(indexed=True)

    print("Building index.")
    build_index(realm.slug)


def reset_index(slug: str) -> None:
    """Reset the index by unmarking the texts as indexed and dropping the collection."""
    realm = Realm.objects.get(slug=slug)
    Text.objects.filter(realm=realm).update(indexed=False)

    drop_collection(realm.slug)


async def store_question(
    question: str, answer: str, prompt: str, texts: List[Text], chatbot: Chatbot
) -> None:
    """Create a new question in the database."""
    question_obj = await Question.objects.acreate(
        question=question, answer=answer, bot=chatbot, prompt=prompt
    )
    await sync_to_async(question_obj.context.set)(texts)


class GlobalCharFilter(GlobalFilter, filters.CharFilter):
    pass


class QuestionGlobalFilter(DatatablesFilterSet):
    """Filter name, artist and genre by name with icontains"""

    question = GlobalCharFilter()

    class Meta:
        model = Question
        fields = ["question", "count"]


class QuestionGlobalViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    filter_backends = (DatatablesFilterBackend,)
    filterset_class = QuestionGlobalFilter

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """
        return Question.objects.filter(bot__slug=self.kwargs["slug"], count__gte=5)
