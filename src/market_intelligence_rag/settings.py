from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    project_root: Path
    data_dir: Path
    manifests_dir: Path
    raw_dir: Path
    processed_dir: Path
    chunks_dir: Path
    benchmarks_dir: Path
    sec_user_agent: str
    openai_api_key: str | None
    qdrant_url: str
    qdrant_collection: str
    embedding_model: str


def get_settings() -> Settings:
    data_dir = PROJECT_ROOT / "data"
    return Settings(
        project_root=PROJECT_ROOT,
        data_dir=data_dir,
        manifests_dir=data_dir / "manifests",
        raw_dir=data_dir / "raw",
        processed_dir=data_dir / "processed",
        chunks_dir=data_dir / "chunks",
        benchmarks_dir=data_dir / "benchmarks",
        sec_user_agent=os.getenv(
            "SEC_USER_AGENT",
            "market-intelligence-rag/0.1 (set SEC_USER_AGENT with contact info)",
        ),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        qdrant_collection=os.getenv(
            "QDRANT_COLLECTION", "market_intelligence_sec_chunks"
        ),
        embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
    )
