from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class CompanySeed:
    company: str
    ticker: str
    cik: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CompanySeed":
        return cls(
            company=data["company"],
            ticker=data["ticker"],
            cik=str(data["cik"]),
        )


@dataclass(frozen=True)
class FormSeed:
    form_type: str
    limit: int
    selected_sections: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FormSeed":
        return cls(
            form_type=data["form_type"],
            limit=int(data.get("limit", 1)),
            selected_sections=list(data.get("selected_sections", [])),
        )


@dataclass(frozen=True)
class ManifestConfig:
    companies: list[CompanySeed]
    forms: list[FormSeed]


@dataclass(frozen=True)
class ManifestEntry:
    company: str
    ticker: str
    cik: str
    form_type: str
    filing_date: str
    accession_number: str
    filing_url: str
    primary_document_url: str
    primary_document_name: str
    period_of_report: str | None = None
    quarter: int | None = None
    year: int | None = None
    selected_sections: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ManifestEntry":
        return cls(
            company=data["company"],
            ticker=data["ticker"],
            cik=str(data["cik"]),
            form_type=data["form_type"],
            filing_date=data["filing_date"],
            accession_number=data["accession_number"],
            filing_url=data["filing_url"],
            primary_document_url=data["primary_document_url"],
            primary_document_name=data["primary_document_name"],
            period_of_report=data.get("period_of_report"),
            quarter=data.get("quarter"),
            year=data.get("year"),
            selected_sections=list(data.get("selected_sections", [])),
        )


@dataclass(frozen=True)
class ProcessedSection:
    section_name: str
    text: str
    char_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProcessedSection":
        return cls(
            section_name=data["section_name"],
            text=data["text"],
            char_count=int(data["char_count"]),
        )


@dataclass(frozen=True)
class ProcessedDocument:
    manifest_entry: ManifestEntry
    sections: list[ProcessedSection]
    processing_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "manifest_entry": self.manifest_entry.to_dict(),
            "sections": [section.to_dict() for section in self.sections],
            "processing_notes": self.processing_notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProcessedDocument":
        return cls(
            manifest_entry=ManifestEntry.from_dict(data["manifest_entry"]),
            sections=[ProcessedSection.from_dict(item) for item in data["sections"]],
            processing_notes=list(data.get("processing_notes", [])),
        )


@dataclass(frozen=True)
class ChunkRecord:
    chunk_id: str
    text: str
    company: str
    ticker: str
    form_type: str
    filing_date: str
    quarter: int | None
    year: int | None
    accession_number: str
    source_url: str
    section_name: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChunkRecord":
        return cls(
            chunk_id=data["chunk_id"],
            text=data["text"],
            company=data["company"],
            ticker=data["ticker"],
            form_type=data["form_type"],
            filing_date=data["filing_date"],
            quarter=data.get("quarter"),
            year=data.get("year"),
            accession_number=data["accession_number"],
            source_url=data["source_url"],
            section_name=data["section_name"],
        )
