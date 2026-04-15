from __future__ import annotations

import re

from .models import ChunkRecord, ProcessedDocument


HEADING_PATTERNS = {
    "mda": (
        r"\bOVERVIEW\b",
        r"\bIndustry Trends and Opportunities\b",
        r"\bReportable Segments\b",
        r"\bResults of Operations\b",
        r"\bLiquidity and Capital Resources\b",
        r"\bOther Planned Uses of Capital\b",
        r"\bCritical Accounting Estimates\b",
    ),
    "risk_factors": (
        r"\bBusiness and Industry Risks\b",
        r"\bRisks Related to Our Business Model\b",
        r"\bLegal and Regulatory Risks\b",
        r"\bOur Expansion into New\b",
    ),
    "exhibit_99_1": (
        r"\bFourth Quarter\s+20\d{2}\b",
        r"\bFirst Quarter\s+20\d{2}\b",
        r"\bSecond Quarter\s+20\d{2}\b",
        r"\bThird Quarter\s+20\d{2}\b",
        r"\bFull Year\s+20\d{2}\b",
        r"\bFinancial Guidance\b",
        r"\bConference Call Information\b",
        r"\bForward-Looking Statements\b",
    ),
}


def chunk_text(text: str, max_chars: int = 1200, overlap_chars: int = 200) -> list[str]:
    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    start_index = 0

    while start_index < len(words):
        chunk_words: list[str] = []
        chunk_len = 0
        cursor = start_index
        while cursor < len(words):
            next_word = words[cursor]
            next_len = len(next_word) + (1 if chunk_words else 0)
            if chunk_words and chunk_len + next_len > max_chars:
                break
            chunk_words.append(next_word)
            chunk_len += next_len
            cursor += 1

        if not chunk_words:
            chunk_words.append(words[cursor])
            cursor += 1

        chunks.append(" ".join(chunk_words))
        if cursor >= len(words):
            break

        overlap_len = 0
        overlap_words = 0
        for word in reversed(chunk_words):
            overlap_len += len(word) + 1
            overlap_words += 1
            if overlap_len >= overlap_chars:
                break

        start_index = max(start_index + 1, cursor - overlap_words)

    return chunks


def build_chunk_records(
    processed_documents: list[ProcessedDocument],
    max_chars: int = 1200,
    overlap_chars: int = 200,
) -> list[ChunkRecord]:
    records: list[ChunkRecord] = []
    for document in processed_documents:
        entry = document.manifest_entry
        for section in document.sections:
            chunk_index = 1
            for block in split_text_for_chunking(section.text, section.section_name):
                for chunk_text_value in chunk_text(
                    block, max_chars=max_chars, overlap_chars=overlap_chars
                ):
                    chunk_id = (
                        f"{entry.ticker.lower()}-"
                        f"{entry.accession_number.replace('-', '')}-"
                        f"{section.section_name}-{chunk_index:03d}"
                    )
                    records.append(
                        ChunkRecord(
                            chunk_id=chunk_id,
                            text=chunk_text_value,
                            company=entry.company,
                            ticker=entry.ticker,
                            form_type=entry.form_type,
                            filing_date=entry.filing_date,
                            quarter=entry.quarter,
                            year=entry.year,
                            accession_number=entry.accession_number,
                            source_url=section.source_url or entry.primary_document_url,
                            section_name=section.section_name,
                        )
                    )
                    chunk_index += 1
    return records


def split_text_for_chunking(text: str, section_name: str) -> list[str]:
    patterns = HEADING_PATTERNS.get(section_name)
    if not patterns:
        return [text]

    matches: list[int] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            if match.start() < 150:
                continue
            matches.append(match.start())

    if not matches:
        return [text]

    split_points = sorted(set(matches))
    blocks: list[str] = []
    start = 0
    for split_point in split_points:
        candidate = text[start:split_point].strip()
        if len(candidate) >= 200:
            blocks.append(candidate)
        start = split_point

    tail = text[start:].strip()
    if tail:
        blocks.append(tail)

    return blocks or [text]
