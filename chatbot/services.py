"""Functions implementing the functionality of the chatbots."""
from django.db.models.query import QuerySet
from tqdm import tqdm

from chatbot.collections import (
    build_index,
    collection_exists,
    create_collection,
    drop_collection,
    insert_embeddings_into,
    search_in_collection,
)
from chatbot.completion import generate_completion
from chatbot.embeddings import batch_embedding, count_tokens, single_embedding
from chatbot.models import Chatbot, Question, Realm, Text


def find_texts(question: str, realm: Realm) -> QuerySet[Text]:
    """Find texts realted to the question."""
    question_embedding = single_embedding(
        question,
        realm.openai_key,
        realm.embedding_model,
        realm.slug,
    )

    text_ids = search_in_collection(question_embedding, realm.slug).ids

    texts = Text.objects.filter(id__in=text_ids)
    return texts


def _format_context(texts: QuerySet[Text], max_tokens: int):
    result = ''

    for text in texts:
        context = f'[{text.id}] {text.content}\n'

        if count_tokens(result + context) > max_tokens:
            return result

        result += context

    return result


def generate_prompt(question: str, texts: QuerySet[Text], chatbot: Chatbot):
    """Generate an answer to the question using the texts and the configuration of the chatbot."""
    prompt_length = count_tokens(chatbot.prompt_template) + count_tokens(question)

    prompt = chatbot.prompt_template.format(
        question=question,
        context=_format_context(texts, chatbot.model_max_tokens - prompt_length - chatbot.max_tokens),
    )

    return prompt


def index_realm(slug: str):
    """Create embedding for each text in the realm and add it to the milvus index."""
    realm = Realm.objects.get(slug=slug)

    texts = Text.objects.filter(realm=realm, indexed=False)

    if not collection_exists(realm.slug):
        create_collection(realm.slug, realm.embedding_dim)

    ids, contents = [], []

    for text in tqdm(texts.iterator(), total=texts.count()):
        ids.append(text.pk)
        contents.append(text.content)
        if len(ids) < 10_000:
            continue
        print("Inserting 10_000 elements.")
        embeddings = batch_embedding(contents, realm.openai_key, realm.embedding_model, realm.slug)
        insert_embeddings_into(ids, embeddings, realm.slug)
        Text.objects.filter(id__in=ids).update(indexed=True)
        ids, contents = [], []

    embeddings = batch_embedding(contents, realm.openai_key, realm.embedding_model, realm.slug)
    insert_embeddings_into(ids, embeddings, realm.slug)

    print("Building index.")
    build_index(realm.slug)


def reset_index(slug: str):
    """Reset the index by unmarking the texts as indexed and dropping the collection."""
    realm = Realm.objects.get(slug=slug)
    Text.objects.filter(realm=realm).update(indexed=False)

    drop_collection(realm.slug)


def store_question(question, answer, prompt, texts, chatbot):
    """Create a new question in the database."""
    question = Question.objects.create(question=question, answer=answer, bot=chatbot, prompt=prompt)
    question.context.set(texts)
