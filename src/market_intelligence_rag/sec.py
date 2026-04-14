from __future__ import annotations

import datetime as dt
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .models import CompanySeed, FormSeed, ManifestEntry, ProcessedDocument, ProcessedSection
from .settings import Settings
from .storage import (
    processed_document_path,
    read_json,
    raw_document_path,
    raw_exhibit_path,
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
                        selected_exhibits=list(form_seed.selected_exhibits),
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
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            response = session.get(entry.primary_document_url, headers=headers, timeout=30)
            response.raise_for_status()
            path.write_text(response.text, encoding="utf-8")
            written_paths.append(path)

        for exhibit in _resolve_selected_exhibits(entry, session, headers):
            exhibit_path = raw_exhibit_path(
                settings, entry, exhibit["exhibit_number"], exhibit["document_name"]
            )
            if exhibit_path.exists() and not force:
                written_paths.append(exhibit_path)
                continue
            exhibit_path.parent.mkdir(parents=True, exist_ok=True)
            exhibit_response = session.get(exhibit["document_url"], headers=headers, timeout=30)
            exhibit_response.raise_for_status()
            exhibit_path.write_text(exhibit_response.text, encoding="utf-8")
            written_paths.append(exhibit_path)

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

        sections: list[ProcessedSection] = []
        notes: list[str] = []
        exhibit_sections = _load_selected_exhibit_sections(entry, settings)
        if exhibit_sections:
            sections.extend(exhibit_sections)
            notes.append(f"Loaded {len(exhibit_sections)} selected exhibits")
        else:
            if entry.selected_exhibits:
                notes.append("Selected exhibits not found; falling back to primary filing document")
            normalized_text = normalize_source_text(raw_path.read_text(encoding="utf-8"))
            extracted_sections, extraction_notes = extract_sections(
                normalized_text,
                entry.selected_sections,
                source_url=entry.primary_document_url,
            )
            sections = extracted_sections
            notes.extend(extraction_notes)
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


def _resolve_selected_exhibits(
    entry: ManifestEntry, session: requests.Session, headers: dict[str, str]
) -> list[dict[str, str]]:
    if not entry.selected_exhibits:
        return []

    response = session.get(entry.filing_url, headers=headers, timeout=30)
    response.raise_for_status()
    return _extract_selected_exhibit_links(response.text, entry.filing_url, entry.selected_exhibits)


def _extract_selected_exhibit_links(
    filing_index_html: str, filing_url: str, selected_exhibits: list[str]
) -> list[dict[str, str]]:
    soup = BeautifulSoup(filing_index_html, "html.parser")
    selected = {_normalize_exhibit_identifier(item) for item in selected_exhibits}
    matches: list[dict[str, str]] = []

    for table in soup.select("table.tableFile"):
        for row in table.select("tr"):
            cells = row.find_all("td")
            if len(cells) < 4:
                continue
            document_link = cells[2].find("a")
            if document_link is None or not document_link.get("href"):
                continue

            exhibit_number = _normalize_exhibit_identifier(cells[3].get_text(" ", strip=True))
            if exhibit_number not in selected:
                continue

            matches.append(
                {
                    "exhibit_number": exhibit_number,
                    "document_name": document_link.get_text(" ", strip=True),
                    "document_url": requests.compat.urljoin(filing_url, document_link["href"]),
                }
            )

    return matches


def _load_selected_exhibit_sections(
    entry: ManifestEntry, settings: Settings
) -> list[ProcessedSection]:
    sections: list[ProcessedSection] = []
    for exhibit_number in entry.selected_exhibits:
        exhibit_glob = (
            f"{entry.accession_number}--{exhibit_number.lower().replace('.', '-')}--*"
        )
        exhibit_dir = raw_document_path(settings, entry).parent
        matches = sorted(exhibit_dir.glob(exhibit_glob))
        if not matches:
            continue
        exhibit_file = matches[0]
        exhibit_text = normalize_source_text(exhibit_file.read_text(encoding="utf-8"))
        document_name = exhibit_file.name.split("--", 2)[-1]
        sections.append(
            ProcessedSection(
                section_name=f"exhibit_{exhibit_number.lower().replace('.', '_')}",
                text=exhibit_text,
                char_count=len(exhibit_text),
                source_url=_build_exhibit_source_url(entry, document_name),
            )
        )
    return sections


def _build_exhibit_source_url(entry: ManifestEntry, document_name: str) -> str:
    return entry.primary_document_url.rsplit("/", 1)[0] + f"/{document_name}"


def _normalize_exhibit_identifier(value: str) -> str:
    normalized = value.strip().upper()
    if normalized.startswith("EX-"):
        normalized = normalized[3:]
    return normalized


def _sec_headers(user_agent: str) -> dict[str, str]:
    return {
        "User-Agent": user_agent,
        "Accept-Encoding": "gzip, deflate",
    }
