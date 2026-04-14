from __future__ import annotations

import datetime as dt
from pathlib import Path

import requests

from .models import CompanySeed, FormSeed, ManifestEntry, ProcessedDocument
from .settings import Settings
from .storage import (
    processed_document_path,
    read_json,
    raw_document_path,
    write_json,
)
from .text_processing import extract_sections, normalize_source_text


SEC_ARCHIVES = "https://www.sec.gov/Archives/edgar/data"
SEC_SUBMISSIONS = "https://data.sec.gov/submissions"


def build_recent_manifest(
    companies: list[CompanySeed], forms: list[FormSeed], settings: Settings
) -> list[ManifestEntry]:
    session = requests.Session()
    headers = _sec_headers(settings.sec_user_agent)
    manifest_entries: list[ManifestEntry] = []

    for company in companies:
        submissions_url = f"{SEC_SUBMISSIONS}/CIK{company.cik.zfill(10)}.json"
        response = session.get(submissions_url, headers=headers, timeout=30)
        response.raise_for_status()
        recent = response.json()["filings"]["recent"]
        rows = list(_recent_rows(recent))
        for form_seed in forms:
            matching_rows = [
                row for row in rows if _row_matches_form_seed(row, form_seed)
            ]
            for row in matching_rows[: form_seed.limit]:
                accession = row["accessionNumber"]
                accession_compact = accession.replace("-", "")
                primary_document = row["primaryDocument"]
                report_date = row.get("reportDate") or None
                quarter, year = infer_period(report_date or row["filingDate"])
                manifest_entries.append(
                    ManifestEntry(
                        company=company.company,
                        ticker=company.ticker,
                        cik=company.cik,
                        form_type=form_seed.form_type,
                        filing_date=row["filingDate"],
                        accession_number=accession,
                        filing_url=(
                            f"{SEC_ARCHIVES}/{int(company.cik)}/"
                            f"{accession_compact}/{accession}-index.htm"
                        ),
                        primary_document_url=(
                            f"{SEC_ARCHIVES}/{int(company.cik)}/"
                            f"{accession_compact}/{primary_document}"
                        ),
                        primary_document_name=primary_document,
                        period_of_report=report_date,
                        quarter=quarter,
                        year=year,
                        selected_sections=list(form_seed.selected_sections),
                    )
                )

    manifest_entries.sort(key=lambda item: (item.filing_date, item.ticker, item.form_type))
    return manifest_entries


def download_manifest_documents(
    entries: list[ManifestEntry], settings: Settings, force: bool = False
) -> list[Path]:
    session = requests.Session()
    headers = _sec_headers(settings.sec_user_agent)
    written_paths: list[Path] = []

    for entry in entries:
        path = raw_document_path(settings, entry)
        if path.exists() and not force:
            written_paths.append(path)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        response = session.get(entry.primary_document_url, headers=headers, timeout=30)
        response.raise_for_status()
        path.write_text(response.text, encoding="utf-8")
        written_paths.append(path)

    return written_paths


def process_manifest_documents(
    entries: list[ManifestEntry], settings: Settings, force: bool = False
) -> list[ProcessedDocument]:
    documents: list[ProcessedDocument] = []

    for entry in entries:
        raw_path = raw_document_path(settings, entry)
        if not raw_path.exists():
            raise FileNotFoundError(
                f"Raw SEC document not found for {entry.ticker} {entry.accession_number}: {raw_path}"
            )

        output_path = processed_document_path(settings, entry)
        if output_path.exists() and not force:
            documents.append(ProcessedDocument.from_dict(read_json(output_path)))
            continue

        normalized_text = normalize_source_text(raw_path.read_text(encoding="utf-8"))
        sections, notes = extract_sections(normalized_text, entry.selected_sections)
        document = ProcessedDocument(
            manifest_entry=entry,
            sections=sections,
            processing_notes=notes,
        )
        write_json(output_path, document.to_dict())
        documents.append(document)

    return documents


def infer_period(date_text: str) -> tuple[int, int]:
    date_value = dt.date.fromisoformat(date_text)
    quarter = ((date_value.month - 1) // 3) + 1
    return quarter, date_value.year


def _recent_rows(recent_filings: dict) -> list[dict[str, str]]:
    size = len(recent_filings["accessionNumber"])
    keys = list(recent_filings.keys())
    rows: list[dict[str, str]] = []
    for index in range(size):
        row: dict[str, str] = {}
        for key in keys:
            values = recent_filings.get(key, [])
            row[key] = values[index] if index < len(values) else ""
        rows.append(row)
    return rows


def _row_matches_form_seed(row: dict[str, str], form_seed: FormSeed) -> bool:
    if row.get("form") != form_seed.form_type:
        return False
    if form_seed.form_type != "8-K":
        return True

    items = row.get("items", "")
    normalized_items = {item.strip() for item in items.split(",") if item.strip()}
    return "2.02" in normalized_items


def _sec_headers(user_agent: str) -> dict[str, str]:
    return {
        "User-Agent": user_agent,
        "Accept-Encoding": "gzip, deflate",
    }
