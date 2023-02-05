"""Methods for working with milvius database."""
from typing import List, cast

import numpy as np
from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    Hits,
    utility,
)


def collection_exists(collection_name: str) -> bool:
    """Indicate whether the collection exists or not."""
    value = utility.has_collection(collection_name)
    assert isinstance(value, bool)
    return value


def list_collections() -> List[str]:
    """List name of all existing collections."""
    value = utility.list_collections()
    return cast(list[str], value)


def count_entries(collection_name: str, flush: bool = False) -> int:
    """Return number of elements in collection."""
    if not collection_exists(collection_name):
        return 0
    collection = Collection(collection_name)
    if flush:
        collection.flush()
    return cast(int, collection.num_entities)


def create_collection(collection_name: str, dim: int = 1536) -> Collection:
    """Create collection fo text."""
    text_id = FieldSchema(name="text_id",
                          dtype=DataType.INT64,
                          is_primary=True)
    text_embedding = FieldSchema(
        name="text_embedding",
        dtype=DataType.FLOAT_VECTOR,
        dim=dim,
    )
    schema = CollectionSchema(fields=[text_id, text_embedding])
    collection = Collection(name=collection_name, schema=schema)

    return collection


def insert_embeddings_into(ids: List[int], embeddings: List[np.ndarray],
                           collection_name: str) -> None:
    """Insert ids with given embeddings into the collection with name realm."""
    if not utility.has_collection(collection_name):
        raise ValueError(
            f"Collection with name {collection_name} does not exist!")
    collection = Collection(name=collection_name)
    collection.insert([ids, embeddings])


def drop_collection(collection_name: str) -> None:
    """Drop collection with the given name."""
    utility.drop_collection(collection_name)


def search_in_collection(embedding, collection_name: str, n: int = 5) -> Hits:
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

    return cast(Hits, results[0])


def build_index(collection_name: str) -> None:
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

    collection.create_index(field_name="text_embedding",
                            index_params=index_params)
