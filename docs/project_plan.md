# Magnificent 7 RAG Project Plan

## Goal

Build a public, interview-ready RAG project over the Magnificent 7 that demonstrates AI data engineering skills relevant to enterprise decision-support products.

## Employer Signal

This project should clearly demonstrate:

- AI-ready data ingestion and preprocessing
- Chunking and embedding workflows
- Vector database usage for semantic retrieval
- Metadata-first design for filtering and traceability
- Source-grounded answers with citations
- Practical trade-off thinking around quality, freshness, and cost

## Scope

### In Scope

- Magnificent 7 company public materials
- Semantic retrieval over unstructured documents
- Metadata filtering by company, date, and document type
- Source-grounded answers with citations
- Lightweight API or CLI interface
- Cheap, persistent deployment path on Oracle VM

### Out of Scope

- Fancy frontend UI
- Large-scale production auth
- Multi-agent orchestration
- Huge corpus ingestion on day one
- Fine-tuned models

## Constraints

- Keep cost as low as possible
- Use recognizable industry tools
- Prefer components that can run on Oracle VM
- Keep the project GitHub-friendly and easy to explain
- Favor clarity over excessive complexity

## Success Criteria

The project is successful if it:

- Ingests a small but useful public corpus for the Magnificent 7
- Chunks and embeds documents reliably
- Stores vectors and metadata in a vector database
- Answers strategic questions with relevant retrieved context
- Returns source citations that are easy to inspect
- Can be explained clearly in an interview in under 3 minutes
- Looks polished and credible on GitHub

## Target User Questions

- How has Microsoft discussed AI monetization over the last 4 quarters?
- What strategic risks has Tesla emphasized recently?
- Which Magnificent 7 companies are talking most about infrastructure investment?
- How have Nvidia and Amazon described capacity constraints differently?
- Which companies are framing AI as efficiency versus revenue growth?

## Architecture Direction

Core flow:

`ingest -> chunk -> embed -> store -> retrieve -> filter/rerank -> prompt -> generate`

Expanded flow:

`ingest -> clean/normalize -> chunk -> embed -> store vectors + metadata -> retrieve -> filter/rerank -> assemble context -> prompt -> generate -> log/evaluate`

## Proposed Stack

- **Language:** Python
- **Vector DB:** Qdrant
- **Embeddings:** OpenAI `text-embedding-3-small`
- **Generation:** Small OpenAI chat model, or retrieval-only in earliest MVP
- **API:** FastAPI
- **Hosting:** Oracle Linux VM
- **Repository:** GitHub

## Data Plan

### Phase 1 Data Sources

Start with the easiest, most reproducible public sources:

- Recent earnings call transcripts, where publicly accessible
- Investor relations press releases
- Shareholder letters
- SEC filings if needed to stabilize source coverage

### MVP Source Strategy

Start narrow:

- 3 companies first: Microsoft, Nvidia, Amazon
- 1 document type first: earnings call transcripts or equivalent strategic text source
- 1 to 2 recent quarters to start

Then expand to all 7 companies.

## Metadata Plan

Each chunk should include:

- `company`
- `ticker`
- `document_type`
- `date`
- `quarter`
- `year`
- `source_url`
- `chunk_id`

Optional later:

- `speaker`
- `section`
- `theme`
- `sentiment_label`

## Risks and Unknowns

- Public transcript sourcing may be inconsistent across companies
- Chunking strategy may affect retrieval quality more than expected
- Retrieval-only MVP may be enough initially, but generated summaries may be needed for stronger demos
- OpenAI API usage should stay small, but costs still need monitoring
- Hosting on Oracle VM is cheap, but deployment should not overcomplicate the first iteration

## Build Phases

### Phase 1: Dataset Definition

- Confirm exact sources for initial 3 companies
- Create document manifest
- Define metadata schema
- Save sample raw documents

### Phase 2: Ingestion Pipeline

- Load documents
- Normalize text
- Extract metadata
- Store raw and processed forms

### Phase 3: Embeddings and Vector Storage

- Implement chunking
- Generate embeddings
- Load vectors into Qdrant
- Verify retrieval manually

### Phase 4: Retrieval Workflow

- Embed user query
- Retrieve top-k chunks
- Apply metadata filters
- Return ranked results with citations

### Phase 5: Generation Layer

- Build grounded prompt from retrieved context
- Generate concise answer
- Return citations alongside answer

### Phase 6: Portfolio Polish

- Write README
- Add architecture diagram
- Add sample queries and outputs
- Document trade-offs, limitations, and future improvements

## GitHub Execution Structure

Use a lightweight GitHub workflow to track delivery without adding unnecessary process.

### Repository Setup

- 1 dedicated GitHub repository for the project
- 1 planning document in this repo for internal design and scope decisions
- 1 GitHub Project board for execution tracking

### Project Board Columns

- `Backlog`
- `Ready`
- `In Progress`
- `Blocked`
- `Done`

### Milestones

- `M1 - Dataset and Scope`
- `M2 - Ingestion Pipeline`
- `M3 - Embeddings and Vector Store`
- `M4 - Retrieval MVP`
- `M5 - Grounded Generation`
- `M6 - Portfolio Polish`

### Labels

- `phase-1`
- `phase-2`
- `phase-3`
- `phase-4`
- `phase-5`
- `phase-6`
- `docs`
- `bug`
- `nice-to-have`

### Initial Issue Strategy

Start with roughly 10 to 15 issues total. Keep issues concrete and outcome-oriented.

Suggested issue areas:

- define initial source strategy and company set
- define metadata schema
- create benchmark questions
- build document manifest and ingestion pipeline
- normalize and store processed text
- implement chunking and embedding generation
- stand up Qdrant and load vectors
- implement retrieval with metadata filters
- add grounded answer generation with citations
- write README and architecture docs

### Process Principles

- Keep the board simple and readable
- Avoid excessive labels, subtasks, or PM ceremony
- Use milestones to group work instead of creating complex hierarchies
- Add new issues only when they are specific and actionable
- Prioritize visible progress over perfect project management

## Decision Log

- Chose Magnificent 7 because it is recognizable, public, and aligns with strategic intelligence use cases
- Chose public company materials over private repo data for easier sharing and portfolio value
- Chose Qdrant over a managed vector DB to keep cost low while still using a recognized tool
- Chose OpenAI embeddings for recognizability and simplicity
- Chose Oracle VM for cheap persistent hosting
- Chose a lightweight GitHub issues and project-board workflow to track execution without overengineering project management

## Open Questions

- Should the MVP start with transcripts only, or combine transcripts with SEC filings?
- Should the first release be retrieval-only, then add generation later?
- Should deployment happen only after local MVP is complete?
- Is Qdrant the final choice, or should Pinecone be considered later for resume signaling?

## Future Improvements

- Hybrid search using keyword + vector retrieval
- Reranking layer for better relevance
- Temporal comparisons across quarters
- Incremental re-indexing when new documents appear
- Docker packaging
- Cloud Run or alternate deployment option
- Lightweight web UI
