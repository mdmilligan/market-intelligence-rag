# SEC Retrieval Evaluation Notes

Artifact reviewed:

- `data/evaluations/sec_retrieval_eval.json`

Model and store:

- embedding model: `text-embedding-3-small`
- vector store: local Qdrant collection `market_intelligence_sec_chunks`

## What Looks Strong

- Targeted company and section queries perform reasonably well.
- Microsoft cloud and AI questions return `10-Q` `mda` chunks with relevant revenue, infrastructure, and AI language.
- Amazon infrastructure and cost questions retrieve useful `mda` chunks that mention fulfillment and infrastructure cost structure.
- NVIDIA demand and supply questions retrieve relevant `risk_factors` and some `mda` chunks tied to AI infrastructure and customer demand.

## What Looks Weak Or Noisy

- Broad comparison queries are weaker than targeted single-company queries.
- Queries such as infrastructure comparison across Microsoft and NVIDIA often return generic business-overview text instead of the most decision-useful evidence.
- Some broad AI-demand questions retrieve partially relevant Microsoft chunks, but not consistently the strongest company-comparison evidence.
- Temporal comparison questions such as changes in Amazon risk disclosures do not yet produce a real diff-oriented answer path; they mostly surface similar chunks from adjacent quarters.
- Several results still include early-section boilerplate or general narrative before the highest-signal operating detail appears.

## Likely Causes

- `10-Q` extraction keeps the full `mda` and `risk_factors` section, so early boilerplate competes with more specific evidence later in the section.
- The current chunking strategy is generic and does not account for subheadings or topic boundaries.
- The corpus still lacks separate `8-K` exhibit ingestion, so earnings-release attachments and shareholder letters are not part of retrieval.
- Broad comparison questions are asking more from pure vector similarity than the current metadata and chunking design supports.

## Recommended Next Changes

1. Trim or skip low-signal `mda` boilerplate at the start of sections where possible.
2. Add heading-aware or subsection-aware chunking so comparison queries hit operating discussion more reliably.
3. Ingest selected `8-K` exhibits such as `99.1` when they contain the real earnings-release narrative.
4. Add a lightweight reranking or heuristic comparison layer only after chunk and source quality improve.
5. Keep broad comparison questions in the benchmark set, but treat them as stretch cases until the corpus is richer.

## Bottom Line

The retrieval stack is working end to end and is already useful for targeted company and section-level questions. The next quality gains are more likely to come from better source coverage and chunk design than from changing the embedding model.
