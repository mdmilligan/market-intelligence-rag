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

## What Looks Weak Or Noisy

- Broad comparison queries are weaker than targeted single-company queries.
- Queries such as infrastructure comparison across Microsoft and NVIDIA still return some generic business-overview text instead of the most decision-useful comparison evidence.
- Some broad AI-demand questions now include better evidence, but they still do not consistently surface the strongest multi-company comparison set.
- Temporal comparison questions such as changes in Amazon risk disclosures do not yet produce a real diff-oriented answer path; they mostly surface similar chunks from adjacent quarters.
- Some `8-K` exhibit chunks still include SEC exhibit header noise such as `EX-99.1` preamble text.
- Several results still include general narrative before the highest-signal operating detail appears.

## Likely Causes

- `10-Q` extraction still keeps large sections, even though the early `mda` boilerplate is now trimmed when possible.
- The current chunking strategy is generic and does not account for subheadings or topic boundaries.
- `8-K` exhibit ingestion now helps materially, but exhibit text still includes some filing-specific header noise.
- Broad comparison questions are asking more from pure vector similarity than the current metadata and chunking design supports.

## Recommended Next Changes

1. Strip `EX-99.1` preamble noise from exhibit text before chunking.
2. Add heading-aware or subsection-aware chunking so comparison queries hit operating discussion more reliably.
3. Consider adding one more targeted `10-Q` subsection or exhibit type only if benchmark results justify it.
4. Add a lightweight reranking or heuristic comparison layer only after chunk and source quality improve.
5. Keep broad comparison questions in the benchmark set, but treat them as stretch cases until the corpus is richer.

## Bottom Line

The retrieval stack is working end to end and is already useful for targeted company and section-level questions. Adding `8-K` `99.1` exhibits materially improved the corpus. The next quality gains are more likely to come from cleaning exhibit text and improving chunk design than from changing the embedding model.
