from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .qdrant_store import search_chunks
from .settings import Settings
from .storage import read_json, write_json


@dataclass(frozen=True)
class BenchmarkQuestion:
    question_id: str
    question: str
    focus: str
    suggested_filters: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BenchmarkQuestion":
        return cls(
            question_id=data["id"],
            question=data["question"],
            focus=data["focus"],
            suggested_filters=dict(data.get("suggested_filters", {})),
        )


def load_benchmark_questions(path: Path) -> list[BenchmarkQuestion]:
    payload = read_json(path)
    return [BenchmarkQuestion.from_dict(item) for item in payload]


def build_retrieval_evaluation(
    questions: list[BenchmarkQuestion], settings: Settings, top_k: int = 3
) -> dict[str, Any]:
    evaluations: list[dict[str, Any]] = []
    for benchmark in questions:
        filters = benchmark.suggested_filters
        results = search_chunks(
            query=benchmark.question,
            settings=settings,
            top_k=top_k,
            company=filters.get("company"),
            form_type=filters.get("form_type"),
            section_name=filters.get("section_name"),
            year=filters.get("year"),
        )
        evaluations.append(
            {
                "id": benchmark.question_id,
                "question": benchmark.question,
                "focus": benchmark.focus,
                "suggested_filters": filters,
                "top_results": [
                    {
                        "rank": index,
                        "score": round(result["score"], 4),
                        "chunk_id": result["payload"]["chunk_id"],
                        "company": result["payload"]["company"],
                        "form_type": result["payload"]["form_type"],
                        "filing_date": result["payload"]["filing_date"],
                        "section_name": result["payload"]["section_name"],
                        "source_url": result["payload"]["source_url"],
                        "snippet": build_result_snippet(result["payload"]["text"]),
                    }
                    for index, result in enumerate(results, start=1)
                ],
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "embedding_model": settings.embedding_model,
        "qdrant_collection": settings.qdrant_collection,
        "question_count": len(questions),
        "results_per_question": top_k,
        "evaluations": evaluations,
    }


def write_retrieval_evaluation(path: Path, evaluation: dict[str, Any]) -> None:
    write_json(path, evaluation)


def build_result_snippet(text: str, max_chars: int = 280) -> str:
    snippet = " ".join(text.split())
    if len(snippet) <= max_chars:
        return snippet
    return snippet[: max_chars - 3].rstrip() + "..."
