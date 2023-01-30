"""Methods for working with milvius database."""
from typing import List

from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    SearchResult,
    utility,
)


def collection_exists(collection_name: str):
    """Indicate whether the collection exists or not."""
    return utility.has_collection(collection_name)


def list_collections():
    """List name of all existing collections."""
    return utility.list_collections()


def count_entries(collection_name: str, flush=False):
    """Return number of elements in collection."""
    if not collection_exists(collection_name):
        return 0
    collection = Collection(collection_name)
    if flush:
        collection.flush()
    return collection.num_entities


def create_collection(collection_name: str, dim=1536):
    """Create collection fo text."""
    text_id = FieldSchema(name="text_id", dtype=DataType.INT64, is_primary=True)
    text_embedding = FieldSchema(
        name="text_embedding",
        dtype=DataType.FLOAT_VECTOR,
        dim=dim,
    )
    schema = CollectionSchema(fields=[text_id, text_embedding])
    collection = Collection(name=collection_name, schema=schema)

    return collection


def insert_embeddings_into(ids, embeddings, collection_name: str):
    """Insert ids with given embeddings into the collection with name realm."""
    if not utility.has_collection(collection_name):
        raise ValueError(f"Collection with name {collection_name} does not exist!")
    collection = Collection(name=collection_name)
    collection.insert([ids, embeddings])


def drop_collection(collection_name: str):
    """Drop collection with the given name."""
    utility.drop_collection(collection_name)


def search_in_collection(embedding, collection_name: str, n=5):
    """Search n close elements to the embedding in the given collection."""
    collection = Collection(name=collection_name)
    collection.load()

    search_params = {'metric_type': 'L2', 'params': {'ef': n * 2}}

    results = collection.search(
        [embedding],
        anns_field='text_embedding',
        param=search_params,
        limit=n,
    )

    return results[0]


def build_index(collection_name: str):
    """Build the index of this collection."""
    collection = Collection(collection_name)

    collection.release()
    collection.drop_index()

    index_params = {
        'metric_type': 'L2',
        'index_type': 'HNSW',
        'params': {
            'M': 64,
            'efConstruction': 128,
        }
    }

    collection.create_index(field_name="text_embedding", index_params=index_params)
