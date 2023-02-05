"""Methods for creating embeddings from texts."""
import logging
import textwrap
from typing import List

import numpy as np
import openai
from transformers import GPT2Tokenizer

from usage.services import store_charge

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

logger = logging.getLogger(__name__)


def count_tokens(text: str) -> int:
    """Count tokens in given text."""
    return len(tokenizer(text)['input_ids'])


async def single_embedding(text: str, openai_key: str, embedding_model: str, user: str, org_id: str = '') -> np.ndarray:
    """Generate a single embedding with model and api key of the realm."""
    response = await openai.Embedding.acreate(
        api_key=openai_key,
        input=text,
        model=embedding_model,
        user=user,
    )
    store_charge(org_id, response)

    return np.array(response['data'][0]['embedding'])


def _chunk_text(texts: List[str], max_tokens=6000) -> List[List[str]]:
    """Generate a list of lists where each inner list contains texts that together are shorter than max_tokens."""
    chunks: List[List[str]] = [[]]
    current_length = 0
    for sentence in texts:
        length = count_tokens(sentence)
        if current_length + length < max_tokens:
            current_length += length
            chunks[-1].append(sentence)
            continue

        if length > max_tokens:
            tokens_per_char = length / len(sentence)
            sentence_length = int((0.75 * max_tokens) / tokens_per_char)
            chunks += [[part] for part in textwrap.wrap(sentence, width=sentence_length)]
            current_length = count_tokens(chunks[-1][0])
            continue

        chunks.append([sentence])
        current_length = length
    return chunks


def batch_embedding(texts: List[str], openai_key: str, embedding_model: str, user: str, org_id: str = '') -> np.ndarray:
    """Generate batch of embeddings for provided texts."""
    results = []
    for chunk in _chunk_text(texts):
        response = openai.Embedding.create(
            api_key=openai_key,
            input=chunk,
            model=embedding_model,
            user=user,
        )
        store_charge(org_id, response)
        results += [data['embedding'] for data in response['data']]

    return np.array(results)
