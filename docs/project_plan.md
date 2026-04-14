# Market Intelligence RAG Architecture

## Purpose

This document captures the durable design decisions for the repository: problem framing, system architecture, source strategy, metadata model, and key trade-offs.

Execution status and task tracking live in the GitHub Project and GitHub Issues, not in this file.

## System Goal

Build a small, credible RAG system over public market intelligence materials that demonstrates practical AI data engineering judgment.

The system is designed to answer strategic questions about how major public companies discuss:

- growth drivers
- risk
- capital investment
- operating constraints
- AI-related themes across quarters

## Scope Boundaries

### In Scope

- Magnificent 7 public company materials
- SEC-first corpus for the initial implementation
- semantic retrieval over unstructured filings
- metadata filtering by company, filing period, form type, and section
- citation-ready retrieval outputs
- CLI-first workflow, with a later path to FastAPI

### Out Of Scope

- fancy frontend UI
- large-scale production auth
- multi-agent orchestration
- broad corpus ingestion on day one
- fine-tuned models

## High-Level Flow

Core architecture:

`ingest -> clean/normalize -> extract sections -> chunk -> embed -> store vectors + metadata -> retrieve -> filter -> cite`

Current repo flow:

`build manifest -> download SEC documents -> normalize -> extract targeted sections -> chunk -> index -> search`

## Source Strategy

### Initial Corpus

Start with the most reproducible public sources:

- SEC `8-K` earnings release materials and attached exhibits
- selected `10-Q` sections for quarterly context
- `10-K` sections only when annual context is needed later

### Initial Company Set

- Microsoft
- NVIDIA
- Amazon

### Initial Section Strategy

The first targeted `10-Q` sections are:

- `mda`
- `risk_factors`

This keeps the initial extraction path narrow while still covering strategy, operating performance, and disclosed risk.

### Expansion Path

After the SEC-first base corpus is stable, the likely next sources are:

- investor relations press releases
- shareholder letters
- other IR website materials that materially improve coverage

## Design Principles

- Favor clarity, credibility, and completeness over complexity
- Use public, reproducible sources first
- Treat metadata as a first-class part of the retrieval design
- Keep the MVP small enough to explain quickly in an interview
- Prefer a strong retrieval pipeline before adding answer generation

## Component Architecture

### Manifest Layer

The manifest layer defines which filings are in scope before ingestion starts.

Responsibilities:

- select companies and form types
- pull recent filing metadata from SEC submissions data
- constrain `8-K` selection toward earnings-related disclosures
- persist a manifest of filing URLs and expected metadata

Primary files:

- `data/manifests/sec_mvp_seeds.json`
- `data/manifests/sec_mvp_manifest.jsonl`
- `src/market_intelligence_rag/manifest.py`
- `src/market_intelligence_rag/sec.py`

### Ingestion Layer

The ingestion layer downloads raw SEC source documents and stores them locally for repeatable runs.

Responsibilities:

- download raw filing documents
- preserve accession-linked source files
- separate raw inputs from processed outputs

Primary files:

- `src/market_intelligence_rag/sec.py`
- `src/market_intelligence_rag/storage.py`

### Normalization And Section Extraction

The normalization layer converts SEC HTML into plain text and extracts targeted filing sections.

Responsibilities:

- strip markup and normalize whitespace
- identify targeted `10-Q` section boundaries
- record processing notes when extraction is weak or missing

Primary files:

- `src/market_intelligence_rag/text_processing.py`

### Chunking Layer

The chunking layer converts processed sections into retrieval-ready text segments.

Responsibilities:

- create overlapping chunks
- preserve source metadata on every chunk
- generate stable chunk identifiers

Primary files:

- `src/market_intelligence_rag/chunking.py`

### Embedding And Vector Storage

The embedding and vector storage layer prepares chunk records for semantic retrieval.

Responsibilities:

- generate embeddings with OpenAI
- store vectors and metadata in Qdrant
- expose filtered semantic search

Primary files:

- `src/market_intelligence_rag/embeddings.py`
- `src/market_intelligence_rag/qdrant_store.py`

### Interface Layer

The initial interface is a CLI. This keeps the early implementation focused on pipeline quality instead of transport concerns.

Responsibilities:

- orchestrate manifest generation, ingestion, processing, chunking, indexing, and search
- remain thin enough that the same core services can later be wrapped by FastAPI

Primary files:

- `src/market_intelligence_rag/cli.py`

## Metadata Model

Each chunk is designed to carry the fields needed for retrieval, filtering, and citation quality.

Current required metadata:

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

Possible later metadata:

- `document_type`
- `period_end`
- `fiscal_period`
- `theme`
- `sentiment_label`

## Storage Layout

The repository separates data by pipeline stage:

- `data/raw/`: raw SEC documents
- `data/processed/`: normalized documents and extracted sections
- `data/chunks/`: chunk records ready for indexing
- `data/manifests/`: manifest seeds and generated manifest files
- `data/benchmarks/`: benchmark retrieval questions

This layout keeps the ingestion pipeline inspectable and makes reruns easier to reason about.

## Retrieval Design

The retrieval layer is built around semantic search plus metadata filtering.

Initial filter dimensions:

- company
- form type
- section name
- year

This supports questions such as:

- how one company discussed AI strategy in recent quarters
- how two companies framed investment differently
- what risk factors changed over time

The design is intentionally metadata-first so results remain explainable and citation-ready.

## Interface Strategy

The project is CLI-first by design.

Why:

- validates the pipeline before adding API surface area
- keeps the first implementation easy to inspect
- reduces early complexity
- makes a later FastAPI wrapper straightforward if core services remain transport-agnostic

Longer term, FastAPI can sit on top of the same ingestion, retrieval, and generation services.

## Key Decisions And Trade-Offs

### SEC-First Instead Of Transcript-First

Chosen because SEC materials are:

- official
- reproducible
- easy to explain
- strong for citation quality

Trade-off:

- less rich in spoken management commentary than earnings call transcripts

### Targeted `10-Q` Sections Instead Of Full Filings

Chosen because full filings are noisy and dilute retrieval quality.

Trade-off:

- section extraction can require filing-specific handling

### CLI First Instead Of FastAPI First

Chosen because it keeps the initial implementation focused on ingestion, metadata, chunking, and retrieval.

Trade-off:

- less product-like presentation in the earliest version

### Retrieval First Before Generation

Chosen because retrieval quality and metadata fidelity are more important than early answer synthesis.

Trade-off:

- the system is not yet a full answering experience

## Risks And Limitations

- SEC filing extraction may still require company-specific handling for some layouts or exhibits
- selected `10-Q` section boundaries may need refinement as coverage expands
- chunking strategy may need iteration to improve retrieval quality
- retrieval quality should be validated carefully before adding grounded answer generation
- the initial corpus is intentionally narrow and does not yet cover all Magnificent 7 companies or all public source types

## Future Directions

- add more companies from the Magnificent 7
- add additional `10-Q` or `10-K` sections where they improve retrieval value
- incorporate IR materials such as shareholder letters and press releases
- validate full Qdrant indexing and filtered retrieval workflow end-to-end
- add grounded answer generation with citations
- add hybrid search or reranking if retrieval quality warrants it
- expose the same core services through FastAPI
