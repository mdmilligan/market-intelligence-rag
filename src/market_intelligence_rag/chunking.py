from __future__ import annotations

from .models import ChunkRecord, ProcessedDocument


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
            for index, chunk_text_value in enumerate(
                chunk_text(section.text, max_chars=max_chars, overlap_chars=overlap_chars),
                start=1,
            ):
                chunk_id = (
                    f"{entry.ticker.lower()}-"
                    f"{entry.accession_number.replace('-', '')}-"
                    f"{section.section_name}-{index:03d}"
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
    return records
