# Market Intelligence RAG

An interview-focused RAG project that turns public Magnificent 7 company materials into a small strategic intelligence copilot.

## What It Does

- ingests public company documents
- chunks and embeds text for semantic retrieval
- stores vectors and metadata in a vector database
- retrieves relevant context for strategic questions
- returns grounded answers with source citations

## Why This Exists

This project is designed to demonstrate practical AI data engineering skills:

- ingestion and preprocessing of unstructured data
- chunking and embedding workflows
- vector database usage
- metadata-first retrieval design
- source-grounded RAG patterns
- trade-off thinking around quality, freshness, and cost

## Initial Scope

The first version focuses on the Magnificent 7:

- Apple
- Microsoft
- Nvidia
- Amazon
- Meta
- Alphabet
- Tesla

Initial data sources will prioritize public strategic materials such as earnings call transcripts, shareholder letters, investor relations releases, and SEC filings.

## Example Questions

- How has Microsoft discussed AI monetization over the last 4 quarters?
- What strategic risks has Tesla emphasized recently?
- Which Magnificent 7 companies are talking most about infrastructure investment?
- How have Nvidia and Amazon described capacity constraints differently?

## Architecture

Core flow:

`ingest -> chunk -> embed -> store -> retrieve -> filter/rerank -> prompt -> generate`

## Planned Stack

- Python
- Qdrant
- OpenAI embeddings
- FastAPI
- Oracle Linux VM

## Project Status

Planning and repository setup.

## Planning Docs

- `docs/project_plan.md`

## Notes

This repo intentionally starts small. The goal is a clear, credible, explainable RAG implementation rather than a flashy demo.
