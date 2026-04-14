from __future__ import annotations

import uuid
from typing import Any

from .embeddings import embed_texts
from .models import ChunkRecord
from .settings import Settings


def index_chunks(chunks: list[ChunkRecord], settings: Settings) -> int:
    if not chunks:
        return 0

    from qdrant_client import QdrantClient
    from qdrant_client.http import models

    vectors = embed_texts(
        [chunk.text for chunk in chunks],
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )
    client = QdrantClient(url=settings.qdrant_url)
    _ensure_collection(client, settings.qdrant_collection, len(vectors[0]))

    points = []
    for chunk, vector in zip(chunks, vectors, strict=True):
        points.append(
            models.PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_URL, chunk.chunk_id)),
                vector=vector,
                payload=chunk.to_dict(),
            )
        )

    client.upsert(collection_name=settings.qdrant_collection, points=points)
    return len(points)


def search_chunks(
    query: str,
    settings: Settings,
    top_k: int = 5,
    company: str | None = None,
    form_type: str | None = None,
    section_name: str | None = None,
    year: int | None = None,
) -> list[dict[str, Any]]:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models

    query_vector = embed_texts(
        [query], model=settings.embedding_model, api_key=settings.openai_api_key
    )[0]
    client = QdrantClient(url=settings.qdrant_url)
    filters = []
    if company:
        filters.append(_match_condition("company", company))
    if form_type:
        filters.append(_match_condition("form_type", form_type))
    if section_name:
        filters.append(_match_condition("section_name", section_name))
    if year is not None:
        filters.append(_match_condition("year", year))

    query_filter = models.Filter(must=filters) if filters else None
    response = client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vector,
        query_filter=query_filter,
        limit=top_k,
    )
    results = response.points
    return [
        {"score": result.score, "payload": result.payload}
        for result in results
    ]


def _ensure_collection(client, collection_name: str, vector_size: int) -> None:
    from qdrant_client.http import models

    collections = [collection.name for collection in client.get_collections().collections]
    if collection_name in collections:
        return
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
    )


def _match_condition(key: str, value: Any):
    from qdrant_client.http import models

    return models.FieldCondition(key=key, match=models.MatchValue(value=value))
