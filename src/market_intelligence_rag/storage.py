from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .models import ChunkRecord, ManifestEntry, ProcessedDocument
from .settings import Settings


def ensure_runtime_dirs(settings: Settings) -> None:
    for path in (
        settings.manifests_dir,
        settings.raw_dir,
        settings.processed_dir,
        settings.chunks_dir,
        settings.benchmarks_dir,
    ):
        path.mkdir(parents=True, exist_ok=True)


def raw_document_path(settings: Settings, entry: ManifestEntry) -> Path:
    suffix = Path(entry.primary_document_name).suffix or ".txt"
    return (
        settings.raw_dir
        / "sec"
        / entry.ticker.lower()
        / entry.form_type.lower()
        / f"{entry.accession_number}{suffix}"
    )


def processed_document_path(settings: Settings, entry: ManifestEntry) -> Path:
    return (
        settings.processed_dir
        / "sec"
        / entry.ticker.lower()
        / entry.form_type.lower()
        / f"{entry.accession_number}.json"
    )


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_processed_documents(
    settings: Settings, entries: Iterable[ManifestEntry]
) -> list[ProcessedDocument]:
    documents: list[ProcessedDocument] = []
    for entry in entries:
        path = processed_document_path(settings, entry)
        if not path.exists():
            continue
        documents.append(ProcessedDocument.from_dict(read_json(path)))
    return documents


def load_chunk_records(path: Path) -> list[ChunkRecord]:
    return [ChunkRecord.from_dict(row) for row in read_jsonl(path)]
