from __future__ import annotations

import argparse
from pathlib import Path

from .chunking import build_chunk_records
from .manifest import load_manifest_entries, load_manifest_seed_config, write_manifest_entries
from .qdrant_store import index_chunks, search_chunks
from .sec import build_recent_manifest, download_manifest_documents, process_manifest_documents
from .settings import get_settings
from .storage import ensure_runtime_dirs, load_chunk_records, load_processed_documents, write_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Market Intelligence RAG CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_manifest = subparsers.add_parser(
        "build-manifest", help="Build a SEC filing manifest from the seed config."
    )
    build_manifest.add_argument(
        "--seed-config",
        type=Path,
        default=Path("data/manifests/sec_mvp_seeds.json"),
    )
    build_manifest.add_argument(
        "--output",
        type=Path,
        default=Path("data/manifests/sec_mvp_manifest.jsonl"),
    )

    ingest_sec = subparsers.add_parser(
        "ingest-sec", help="Download raw SEC documents from a manifest."
    )
    ingest_sec.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/manifests/sec_mvp_manifest.jsonl"),
    )
    ingest_sec.add_argument("--force", action="store_true")

    process_sec = subparsers.add_parser(
        "process-sec", help="Normalize raw SEC documents and extract sections."
    )
    process_sec.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/manifests/sec_mvp_manifest.jsonl"),
    )
    process_sec.add_argument("--force", action="store_true")

    chunk_sec = subparsers.add_parser(
        "chunk-sec", help="Chunk processed SEC documents into retrieval records."
    )
    chunk_sec.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/manifests/sec_mvp_manifest.jsonl"),
    )
    chunk_sec.add_argument(
        "--output",
        type=Path,
        default=Path("data/chunks/sec_chunks.jsonl"),
    )
    chunk_sec.add_argument("--max-chars", type=int, default=1200)
    chunk_sec.add_argument("--overlap-chars", type=int, default=200)

    index_qdrant = subparsers.add_parser(
        "index-qdrant", help="Embed and load chunk records into Qdrant."
    )
    index_qdrant.add_argument(
        "--chunks",
        type=Path,
        default=Path("data/chunks/sec_chunks.jsonl"),
    )

    search_qdrant = subparsers.add_parser(
        "search-qdrant", help="Run a semantic search against indexed SEC chunks."
    )
    search_qdrant.add_argument("--query", required=True)
    search_qdrant.add_argument("--top-k", type=int, default=5)
    search_qdrant.add_argument("--company")
    search_qdrant.add_argument("--form-type")
    search_qdrant.add_argument("--section-name")
    search_qdrant.add_argument("--year", type=int)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    settings = get_settings()
    ensure_runtime_dirs(settings)

    if args.command == "build-manifest":
        config = load_manifest_seed_config(args.seed_config)
        manifest_entries = build_recent_manifest(config.companies, config.forms, settings)
        write_manifest_entries(args.output, manifest_entries)
        print(f"Wrote {len(manifest_entries)} manifest entries to {args.output}")
        return

    if args.command == "ingest-sec":
        entries = load_manifest_entries(args.manifest)
        paths = download_manifest_documents(entries, settings, force=args.force)
        print(f"Downloaded {len(paths)} SEC documents")
        return

    if args.command == "process-sec":
        entries = load_manifest_entries(args.manifest)
        documents = process_manifest_documents(entries, settings, force=args.force)
        extracted_sections = sum(len(document.sections) for document in documents)
        print(
            f"Processed {len(documents)} documents and extracted {extracted_sections} sections"
        )
        return

    if args.command == "chunk-sec":
        entries = load_manifest_entries(args.manifest)
        documents = load_processed_documents(settings, entries)
        records = build_chunk_records(
            documents,
            max_chars=args.max_chars,
            overlap_chars=args.overlap_chars,
        )
        write_jsonl(args.output, [record.to_dict() for record in records])
        print(f"Wrote {len(records)} chunks to {args.output}")
        return

    if args.command == "index-qdrant":
        chunks = load_chunk_records(args.chunks)
        count = index_chunks(chunks, settings)
        print(f"Indexed {count} chunks into Qdrant")
        return

    if args.command == "search-qdrant":
        results = search_chunks(
            query=args.query,
            settings=settings,
            top_k=args.top_k,
            company=args.company,
            form_type=args.form_type,
            section_name=args.section_name,
            year=args.year,
        )
        for result in results:
            payload = result["payload"]
            print(
                f"[{result['score']:.3f}] {payload['company']} {payload['form_type']} "
                f"{payload['filing_date']} {payload['section_name']} {payload['source_url']}"
            )
        return

    parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
