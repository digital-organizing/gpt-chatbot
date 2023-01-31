"""Tests for the chatbot application."""
from os import environ

import numpy as np
from django.test import TestCase

from chatbot.collections import (
    build_index,
    collection_exists,
    count_entries,
    create_collection,
    drop_collection,
    insert_embeddings_into,
    list_collections,
    search_in_collection,
)
from chatbot.embeddings import batch_embedding, single_embedding

openai_key = environ.get('OPENAI_API_KEY', '')
openai_user = 'testing'
openai_model = 'text-embedding-ada-002'


class TestEmbedding(TestCase):
    """Test cases for embeddings."""

    async def test_single_embedding(self):
        """Test creating an embedding from a single text."""
        embedding = await single_embedding("This is a simple test.", openai_key, openai_model, openai_user)
        self.assertIsNotNone(embedding)
        self.assertEqual(1536, embedding.shape[0])

    def test_batch_embedding(self):
        """Test creating embeddings from a batch of texts."""
        batch_texts = ['This is a first test', 'This is a second text', 'This is a third text']
        embeddings = batch_embedding(batch_texts, openai_key, openai_model, openai_user)
        self.assertEqual(len(batch_texts), len(embeddings))


class TestCollection(TestCase):
    """Test collection methods."""

    texts = ["Tom is a brown dog.", "Garfield is a yellow cat.", "Birds fly to the south in winter."]

    def tearDown(self):
        """Drop all test collections."""
        for collection in list_collections():
            if collection.startswith('test_'):
                drop_collection(collection)

    def test_create_collection(self):
        """Test creating an empty collection."""
        create_collection('test_create')
        self.assertTrue(collection_exists('test_create'))

    def test_add_embeddings(self):
        """Test adding embeddings to a collection."""
        embeddings = batch_embedding(self.texts, openai_key, openai_model, openai_user)
        ids = np.arange(len(embeddings))

        create_collection('test_insert')
        insert_embeddings_into(ids, embeddings, 'test_insert')

        self.assertEqual(len(embeddings), count_entries('test_insert', True))

    def test_create_index(self):
        """Test building an index."""
        embeddings = batch_embedding(self.texts, openai_key, openai_model, openai_user)
        ids = np.arange(len(embeddings))

        create_collection('test_index')
        insert_embeddings_into(ids, embeddings, 'test_index')
        build_index('test_index')

    async def test_search_texts(self):
        """Test searching texts in an indexed collection."""
        embeddings = batch_embedding(self.texts, openai_key, openai_model, openai_user)
        ids = np.arange(len(embeddings))

        create_collection('test_search')
        insert_embeddings_into(ids, embeddings, 'test_search')
        build_index('test_search')

        query_embedding = await single_embedding('Where do bird go in winter?', openai_key, openai_model, openai_user)

        result = search_in_collection(query_embedding, 'test_search', n=1)
        self.assertEqual(2, result.ids[0])
