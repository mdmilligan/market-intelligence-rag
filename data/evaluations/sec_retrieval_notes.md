# SEC Retrieval Evaluation Notes

Artifact reviewed:

- `data/evaluations/sec_retrieval_eval.json`

Model and store:

- embedding model: `text-embedding-3-small`
- vector store: local Qdrant collection `market_intelligence_sec_chunks`

## What Looks Strong

- Targeted company and section queries perform reasonably well.
- Microsoft cloud and AI questions now retrieve both `10-Q` `mda` evidence and `8-K` `99.1` earnings-release language.
- Amazon infrastructure and cost questions retrieve both `10-Q` risk language and `8-K` `99.1` earnings-release narrative.
- NVIDIA demand and supply questions retrieve relevant `8-K` `99.1` earnings-release chunks as well as `risk_factors` tied to AI infrastructure and customer demand.
- Broad infrastructure questions improved after adding `99.1` exhibits; Amazon capital expenditure commentary now appears directly in top results.
- Trimming early `mda` boilerplate improved the quality of Microsoft `10-Q` snippets and moved more operating discussion into early chunk ranks.
- Stripping `EX-99.1` preamble noise makes earnings-release chunks read like real narrative instead of filing artifacts.
- Heading-aware chunking now surfaces sections like `Other Planned Uses of Capital` more directly for capital-investment questions.

## What Looks Weak Or Noisy

- Broad comparison queries are weaker than targeted single-company queries.
- Queries such as infrastructure comparison across Microsoft and NVIDIA still return some generic business-overview text instead of the most decision-useful comparison evidence.
- Some broad AI-demand questions now include better evidence, but they still do not consistently surface the strongest multi-company comparison set.
- Temporal comparison questions such as changes in Amazon risk disclosures do not yet produce a real diff-oriented answer path; they mostly surface similar chunks from adjacent quarters.
- Several results still include general narrative before the highest-signal operating detail appears.

## Likely Causes

- `10-Q` extraction still keeps large sections, even though the early `mda` boilerplate is now trimmed when possible.
- Heading-aware chunking improves targeting, but broad comparison questions still ask more from vector similarity than a single-stage retriever can reliably deliver.
- Broad comparison questions are asking more from pure vector similarity than the current metadata and chunking design supports.

## Recommended Next Changes

1. Add a lightweight reranking or heuristic comparison layer for broad multi-company questions.
2. Consider adding one more targeted `10-Q` subsection or exhibit type only if benchmark results justify it.
3. Explore a small temporal-comparison helper for quarter-over-quarter risk-change questions.
4. Keep broad comparison questions in the benchmark set, but treat them as stretch cases until the corpus is richer.

## Bottom Line

The retrieval stack is working end to end and is already useful for targeted company and section-level questions. Adding `8-K` `99.1` exhibits materially improved the corpus. The next quality gains are more likely to come from cleaning exhibit text and improving chunk design than from changing the embedding model.
