from __future__ import annotations

from pathlib import Path

from .models import CompanySeed, FormSeed, ManifestConfig, ManifestEntry
from .storage import read_json, read_jsonl, write_jsonl


def load_manifest_seed_config(path: Path) -> ManifestConfig:
    payload = read_json(path)
    return ManifestConfig(
        companies=[CompanySeed.from_dict(item) for item in payload["companies"]],
        forms=[FormSeed.from_dict(item) for item in payload["forms"]],
    )


def load_manifest_entries(path: Path) -> list[ManifestEntry]:
    return [ManifestEntry.from_dict(row) for row in read_jsonl(path)]


def write_manifest_entries(path: Path, entries: list[ManifestEntry]) -> None:
    write_jsonl(path, [entry.to_dict() for entry in entries])
