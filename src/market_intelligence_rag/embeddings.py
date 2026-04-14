from __future__ import annotations

from typing import Iterable


def embed_texts(texts: Iterable[str], model: str, api_key: str | None) -> list[list[float]]:
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required for embedding generation.")

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.embeddings.create(model=model, input=list(texts))
    return [item.embedding for item in response.data]
