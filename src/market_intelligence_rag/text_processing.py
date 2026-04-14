from __future__ import annotations

import html
import re
from dataclasses import dataclass

from bs4 import BeautifulSoup

from .models import ProcessedSection


@dataclass(frozen=True)
class SectionPattern:
    section_name: str
    start_patterns: tuple[str, ...]
    end_patterns: tuple[str, ...]


SECTION_PATTERNS = {
    "mda": SectionPattern(
        section_name="mda",
        start_patterns=(
            r"part\s*i\s*item\s*2\.?\s*management.{0,40}?discussion\s*and\s*analysis",
            r"item\s*2\.?\s*management.{0,40}?discussion\s*and\s*analysis",
        ),
        end_patterns=(
            r"part\s*i\s*item\s*3\.?\s*quantitative\s*and\s*qualitative\s*disclosures",
            r"item\s*3\.?\s*quantitative\s*and\s*qualitative\s*disclosures",
            r"part\s*ii\s*item\s*1\.?\s*legal\s*proceedings",
            r"part\s*ii\s*item\s*1a\.?\s*risk\s*factors",
        ),
    ),
    "risk_factors": SectionPattern(
        section_name="risk_factors",
        start_patterns=(
            r"part\s*ii\s*item\s*1a\.?\s*risk\s*factors",
            r"item\s*1a\.?\s*risk\s*factors",
        ),
        end_patterns=(
            r"part\s*ii\s*item\s*2\.?\s*unregistered\s*sales",
            r"item\s*2\.?\s*unregistered\s*sales",
            r"part\s*ii\s*item\s*5\.?\s*other\s*information",
            r"item\s*5\.?\s*other\s*information",
            r"signatures",
        ),
    ),
}


def normalize_source_text(source_text: str) -> str:
    text = source_text
    if "<html" in source_text.lower() or "<body" in source_text.lower():
        soup = BeautifulSoup(source_text, "html.parser")
        for element in soup(["script", "style", "noscript"]):
            element.decompose()
        text = soup.get_text("\n")

    text = html.unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\s*\n\s*", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_sections(text: str, selected_sections: list[str]) -> tuple[list[ProcessedSection], list[str]]:
    sections: list[ProcessedSection] = []
    notes: list[str] = []

    if not selected_sections:
        sections.append(
            ProcessedSection(
                section_name="filing_document",
                text=text,
                char_count=len(text),
            )
        )
        return sections, notes

    lowered = text.lower()
    for section_key in selected_sections:
        pattern = SECTION_PATTERNS.get(section_key)
        if pattern is None:
            notes.append(f"Unknown section pattern: {section_key}")
            continue

        candidates: list[str] = []
        for start_match in _all_matches(lowered, pattern.start_patterns):
            end_index = len(text)
            tail = lowered[start_match.end() :]
            for end_pattern in pattern.end_patterns:
                end_match = re.search(end_pattern, tail, re.IGNORECASE)
                if end_match:
                    end_index = min(end_index, start_match.end() + end_match.start())

            if end_index <= start_match.start():
                continue

            section_text = text[start_match.start() : end_index].strip()
            if section_text:
                candidates.append(section_text)

        if not candidates:
            notes.append(f"Section not found: {section_key}")
            continue

        section_text = max(candidates, key=len)
        if len(section_text) < 200:
            notes.append(f"Section too short after extraction: {section_key}")
            continue

        sections.append(
            ProcessedSection(
                section_name=pattern.section_name,
                text=section_text,
                char_count=len(section_text),
            )
        )

    return sections, notes


def _all_matches(text: str, patterns: tuple[str, ...]) -> list[re.Match[str]]:
    matches: list[re.Match[str]] = []
    for pattern in patterns:
        matches.extend(re.finditer(pattern, text, re.IGNORECASE))
    matches.sort(key=lambda match: match.start())
    return matches
