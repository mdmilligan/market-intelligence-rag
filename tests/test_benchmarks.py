from market_intelligence_rag.benchmarks import BenchmarkQuestion, build_result_snippet


def test_benchmark_question_from_dict() -> None:
    question = BenchmarkQuestion.from_dict(
        {
            "id": "q1",
            "question": "How is Microsoft describing AI demand?",
            "focus": "strategy",
            "suggested_filters": {"company": "Microsoft"},
        }
    )
    assert question.question_id == "q1"
    assert question.suggested_filters == {"company": "Microsoft"}


def test_build_result_snippet_truncates_cleanly() -> None:
    text = " ".join(f"word{i}" for i in range(100))
    snippet = build_result_snippet(text, max_chars=40)
    assert snippet.endswith("...")
    assert len(snippet) <= 40
