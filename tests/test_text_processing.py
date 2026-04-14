from market_intelligence_rag.chunking import chunk_text
from market_intelligence_rag.text_processing import extract_sections, normalize_source_text


def test_normalize_source_text_strips_html() -> None:
    html = "<html><body><h1>Title</h1><p>Hello&nbsp;world</p></body></html>"
    normalized = normalize_source_text(html)
    assert normalized == "Title Hello world"


def test_extract_sections_pulls_targeted_10q_sections() -> None:
    text = (
        "Part I Item 2. Management's Discussion and Analysis of Financial Condition and Results of Operations "
        + ("Revenue grew strongly due to cloud demand. " * 20)
        + "Part I Item 3. Quantitative and Qualitative Disclosures About Market Risk "
        + "Part II Item 1A. Risk Factors "
        + ("Supply chain concentration remains a material risk. " * 20)
        + "Part II Item 2. Unregistered Sales of Equity Securities and Use of Proceeds"
    )
    sections, notes = extract_sections(text, ["mda", "risk_factors"])
    assert [section.section_name for section in sections] == ["mda", "risk_factors"]
    assert notes == []


def test_extract_sections_skips_table_of_contents_match() -> None:
    text = (
        "Part I Item 2. Management's Discussion and Analysis of Financial Condition and Results of Operations "
        "Part I Item 3. Quantitative and Qualitative Disclosures About Market Risk "
        "Part I Item 2. Management's Discussion and Analysis of Financial Condition and Results of Operations "
        + ("Azure revenue and AI demand grew. " * 30)
        + "Part I Item 3. Quantitative and Qualitative Disclosures About Market Risk"
    )
    sections, notes = extract_sections(text, ["mda"])
    assert len(sections) == 1
    assert "Azure revenue and AI demand grew." in sections[0].text
    assert notes == []


def test_extract_sections_trims_mda_boilerplate() -> None:
    text = (
        "Part I Item 2. Management's Discussion and Analysis of Financial Condition and Results of Operations "
        "Forward-Looking Statements This Quarterly Report includes forward-looking statements within the meaning of the Private Securities Litigation Reform Act of 1995. "
        "Critical Accounting Estimates Some introductory boilerplate applies. "
        "Overview Azure revenue grew due to AI and cloud demand while infrastructure investments increased. "
        + ("Overview Azure revenue grew due to AI and cloud demand while infrastructure investments increased. " * 15)
        + "Part I Item 3. Quantitative and Qualitative Disclosures About Market Risk"
    )
    sections, notes = extract_sections(text, ["mda"])
    assert len(sections) == 1
    assert sections[0].text.startswith("Overview Azure revenue grew")
    assert any("Trimmed low-signal MDA boilerplate" in note for note in notes)



def test_chunk_text_uses_overlap() -> None:
    text = " ".join(f"word{i}" for i in range(250))
    chunks = chunk_text(text, max_chars=120, overlap_chars=25)
    assert len(chunks) > 1
    assert chunks[0].split()[-1] in chunks[1].split()
