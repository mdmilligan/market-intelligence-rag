from __future__ import annotations

from typing import Any

from openai import OpenAI

from .qdrant_store import search_chunks
from .settings import Settings


WEAK_RETRIEVAL_SCORE_THRESHOLD = 0.45


def answer_question(
    query: str,
    settings: Settings,
    top_k: int = 5,
    company: str | None = None,
    form_type: str | None = None,
    section_name: str | None = None,
    year: int | None = None,
) -> dict[str, Any]:
    results = search_chunks(
        query=query,
        settings=settings,
        top_k=top_k,
        company=company,
        form_type=form_type,
        section_name=section_name,
        year=year,
    )
    citations = build_citation_list(results)
    if is_weak_retrieval(results):
        return {
            "answer": (
                "I do not have enough high-confidence retrieved evidence to answer this reliably yet. "
                "Review the citations below and refine the query or filters."
            ),
            "citations": citations,
            "retrieval_results": results,
            "weak_retrieval": True,
        }

    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required for grounded answer generation.")

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.chat_model,
        temperature=0.1,
        max_tokens=500,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful financial research assistant. Answer only from the provided SEC excerpts. "
                    "Do not use outside knowledge. Use inline citations like [1] and [2] tied to the provided sources. "
                    "If evidence is mixed or limited, say so clearly."
                ),
            },
            {
                "role": "user",
                "content": build_answer_prompt(query, citations),
            },
        ],
    )
    answer = response.choices[0].message.content or "No answer generated."
    return {
        "answer": answer.strip(),
        "citations": citations,
        "retrieval_results": results,
        "weak_retrieval": False,
    }


def build_answer_prompt(query: str, citations: list[dict[str, Any]]) -> str:
    prompt_lines = [
        f"Question: {query}",
        "",
        "Use only the sources below.",
        "Cite claims inline with bracketed source numbers.",
        "",
        "Sources:",
    ]
    for citation in citations:
        prompt_lines.extend(
            [
                (
                    f"[{citation['index']}] {citation['company']} | {citation['form_type']} | "
                    f"{citation['filing_date']} | {citation['section_name']}"
                ),
                f"Source URL: {citation['source_url']}",
                f"Text: {citation['text']}",
                "",
            ]
        )
    return "\n".join(prompt_lines).strip()


def build_citation_list(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []
    for index, result in enumerate(results, start=1):
        payload = result["payload"]
        citations.append(
            {
                "index": index,
                "chunk_id": payload["chunk_id"],
                "company": payload["company"],
                "form_type": payload["form_type"],
                "filing_date": payload["filing_date"],
                "section_name": payload["section_name"],
                "source_url": payload["source_url"],
                "score": round(result["score"], 4),
                "text": payload["text"],
            }
        )
    return citations


def is_weak_retrieval(results: list[dict[str, Any]]) -> bool:
    if not results:
        return True
    return results[0]["score"] < WEAK_RETRIEVAL_SCORE_THRESHOLD
