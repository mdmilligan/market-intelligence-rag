from market_intelligence_rag.generation import (
    build_answer_prompt,
    build_citation_list,
    is_weak_retrieval,
)


def test_build_citation_list_preserves_metadata() -> None:
    citations = build_citation_list(
        [
            {
                "score": 0.62,
                "payload": {
                    "chunk_id": "msft-1",
                    "company": "Microsoft",
                    "form_type": "10-Q",
                    "filing_date": "2026-01-28",
                    "section_name": "mda",
                    "source_url": "https://example.com/msft",
                    "text": "Sample text",
                },
            }
        ]
    )
    assert citations[0]["index"] == 1
    assert citations[0]["chunk_id"] == "msft-1"
    assert citations[0]["score"] == 0.62


def test_build_answer_prompt_includes_numbered_sources() -> None:
    prompt = build_answer_prompt(
        "How is Microsoft describing AI demand?",
        [
            {
                "index": 1,
                "company": "Microsoft",
                "form_type": "8-K",
                "filing_date": "2026-01-28",
                "section_name": "exhibit_99_1",
                "source_url": "https://example.com/msft",
                "text": "Microsoft Cloud and AI Strength Drives Second Quarter Results.",
            }
        ],
    )
    assert "Question: How is Microsoft describing AI demand?" in prompt
    assert "[1] Microsoft | 8-K | 2026-01-28 | exhibit_99_1" in prompt
    assert "Microsoft Cloud and AI Strength Drives Second Quarter Results." in prompt


def test_is_weak_retrieval_flags_low_scores() -> None:
    assert is_weak_retrieval([]) is True
    assert is_weak_retrieval([{"score": 0.44, "payload": {}}]) is True
    assert is_weak_retrieval([{"score": 0.55, "payload": {}}]) is False
