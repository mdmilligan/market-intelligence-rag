# Market Intelligence RAG

A source-grounded RAG system over SEC earnings materials for analyzing how major public companies discuss strategy, risk, and investment across quarters.

## Why This Project Exists

Many RAG projects optimize for a generic chat experience over arbitrary text. This project is intentionally narrower.

The goal is to build a small but credible retrieval system over public market data that:

- ingests reproducible SEC materials
- preserves metadata needed for filtering and traceability
- retrieves context for strategic questions
- supports citation-ready outputs instead of vague summaries

The scope is intentionally focused to highlight practical AI data engineering judgment: source selection, metadata design, ingestion quality, and grounded retrieval.

## What The System Does

- builds a small SEC-first corpus for Magnificent 7 companies
- extracts targeted quarterly earnings material from `8-K` and `10-Q` filings
- normalizes filing text and preserves citation metadata
- chunks documents into retrieval-ready records
- supports semantic retrieval with metadata filters
- supports a retrieval-first pipeline with a clear path to grounded answer generation

## Current Scope

Current scope:

- source base: SEC materials first
- starting companies: Microsoft, NVIDIA, Amazon
- filing types: earnings-related `8-K` materials plus selected `10-Q` sections
- selected `10-Q` sections: `mda` and `risk_factors`
- interface: CLI first, with a later path to FastAPI

Why this scope:

- SEC filings are official, reproducible, and easy to explain
- targeted `10-Q` extraction gives better signal than full-filing ingestion
- CLI keeps the first version focused on ingestion, metadata, retrieval, and citations

## Architecture

Core flow:

`ingest -> clean/normalize -> extract sections -> chunk -> embed -> store vectors + metadata -> retrieve -> filter -> cite`

Current implementation is centered around a manifest-driven SEC workflow:

1. build a filing manifest from SEC submissions data
2. download raw SEC documents
3. normalize filing text and extract targeted sections
4. chunk processed text into citation-ready records
5. optionally embed and index chunks into Qdrant
6. query with metadata filters such as company, form type, section, and year

## Data And Metadata Design

Each chunk is designed to carry the metadata needed for retrieval and citation quality.

Current chunk metadata includes:

- `company`
- `ticker`
- `form_type`
- `filing_date`
- `quarter`
- `year`
- `accession_number`
- `source_url`
- `section_name`
- `chunk_id`

This metadata-first design is a core part of the project. The point is not only to retrieve similar text, but to preserve enough structure to support:

- citation
- filtering
- explainability
- future governance-style controls

## Example Questions

- How has Microsoft discussed AI monetization in recent quarterly materials?
- What risks has Amazon highlighted around fulfillment capacity and operating costs?
- How do Microsoft and NVIDIA describe infrastructure investment differently?
- Which quarterly earnings materials mention efficiency gains versus revenue growth from AI?

The benchmark question set for repeatable retrieval checks lives in `data/benchmarks/sec_retrieval_questions.json`.

## Current Capabilities

- SEC seed config and benchmark scaffolding
- live SEC manifest generation for the initial company set
- raw document download from SEC
- filing normalization and targeted `10-Q` section extraction
- chunk generation for retrieval
- Qdrant indexing and semantic search commands
- tests for normalization, section extraction, and chunk overlap

Execution status and next steps are tracked in GitHub Issues and the GitHub Project.

## Repository Layout

- `src/market_intelligence_rag/`: CLI, SEC ingestion, processing, chunking, and retrieval code
- `data/manifests/`: seed config and generated SEC filing manifest
- `data/benchmarks/`: benchmark questions for retrieval evaluation
- `docs/project_plan.md`: architecture and design reference
- `tests/`: focused tests for text processing and chunking behavior

## Local Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project and development dependencies:

```bash
pip install -r requirements.txt
pip install -e .
```

Local configuration is loaded automatically from `.env` via `python-dotenv`.

Tracked template:

```bash
.env.example
```

Local file:

```bash
.env
```

Set a valid SEC user agent and, when needed, your OpenAI key in `.env` before running the pipeline.

Main settings:

- `OPENAI_API_KEY`: required for embedding and semantic search
- `QDRANT_URL`: defaults to `http://localhost:6333`
- `QDRANT_COLLECTION`: defaults to `market_intelligence_sec_chunks`
- `EMBEDDING_MODEL`: defaults to `text-embedding-3-small`

## Running The Pipeline

Build the filing manifest:

```bash
market-rag build-manifest
```

Download raw SEC documents:

```bash
market-rag ingest-sec
```

Normalize filings and extract targeted sections:

```bash
market-rag process-sec
```

Chunk processed documents:

```bash
market-rag chunk-sec
```

Optional indexing and retrieval flow after configuring Qdrant and `OPENAI_API_KEY`:

```bash
market-rag index-qdrant
market-rag search-qdrant --query "How is Microsoft describing AI demand?"
```

## Tradeoffs And Limitations

- SEC-first sourcing is more reproducible than transcript-first sourcing, but less rich in spoken management commentary
- targeted section extraction improves signal, but some filings still require company-specific handling
- the current system is retrieval-first; grounded answer generation is not complete yet
- the initial corpus is intentionally narrow so the project stays explainable and easy to inspect

## What This Demonstrates

This project demonstrates the parts of RAG work that matter in real systems:

- source selection and reproducibility
- metadata design
- ingestion and normalization quality
- retrieval quality over unstructured text
- citation-ready outputs
- honest scope control

The project is intentionally optimized for clarity, credibility, and maintainability over hype.
