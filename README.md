# Market Intelligence RAG

CLI-first SEC market intelligence RAG project focused on a small, credible retrieval pipeline over Magnificent 7 public company materials.

## Current MVP Direction

- SEC-first corpus
- 3 starting companies: Microsoft, NVIDIA, Amazon
- `8-K` earnings-release materials plus selected `10-Q` sections
- selected `10-Q` sections: `mda` and `risk_factors`
- metadata-first chunking and citation design
- CLI first, with a later path to FastAPI

## What Exists Now

- SEC seed config in `data/manifests/sec_mvp_seeds.json`
- benchmark question set in `data/benchmarks/sec_retrieval_questions.json`
- CLI commands to:
  - build a live SEC manifest
  - download raw SEC documents
  - normalize filings and extract targeted sections
  - chunk processed text into citation-ready records
  - index and search chunks with OpenAI embeddings and Qdrant
- tests for normalization, section extraction, and chunk overlap

## Repository Layout

- `src/market_intelligence_rag/`: core CLI, SEC ingestion, normalization, chunking, and retrieval code
- `data/manifests/`: versioned manifest seed config and generated SEC manifest
- `data/benchmarks/`: repeatable retrieval questions
- `docs/project_plan.md`: project scope, decisions, and phased plan

## Local Workflow

Set a SEC user agent first:

```bash
export SEC_USER_AGENT="market-intelligence-rag your-email@example.com"
```

Build the manifest:

```bash
PYTHONPATH=src python3 -m market_intelligence_rag.cli build-manifest
```

Download raw SEC documents:

```bash
PYTHONPATH=src python3 -m market_intelligence_rag.cli ingest-sec
```

Normalize and extract sections:

```bash
PYTHONPATH=src python3 -m market_intelligence_rag.cli process-sec
```

Chunk processed documents:

```bash
PYTHONPATH=src python3 -m market_intelligence_rag.cli chunk-sec
```

Optional retrieval commands after setting `OPENAI_API_KEY` and running Qdrant:

```bash
PYTHONPATH=src python3 -m market_intelligence_rag.cli index-qdrant
PYTHONPATH=src python3 -m market_intelligence_rag.cli search-qdrant --query "How is Microsoft describing AI demand?"
```

## Environment

- `SEC_USER_AGENT`: required for polite SEC access
- `OPENAI_API_KEY`: required for embedding and semantic search
- `QDRANT_URL`: optional, defaults to `http://localhost:6333`
- `QDRANT_COLLECTION`: optional, defaults to `market_intelligence_sec_chunks`

## Current Status

- working SEC manifest generation against live SEC submissions data
- working raw download, normalization, section extraction, and chunk generation
- Qdrant indexing and semantic search commands are implemented, but still need full end-to-end validation in this repo
- grounded answer generation and portfolio polish are still ahead

## Notes

This repo is intentionally narrow. The goal is to demonstrate practical AI data engineering judgment, not a generic chatbot demo.
