"""
Day 5: minimal test suite. Extend as each module gets built.
"""
from app.utils.text_utils import clean_text, split_into_clauses


def test_clean_text_collapses_whitespace():
    raw = "Hello   world\r\n\r\n\r\nThis is  a test."
    cleaned = clean_text(raw)
    assert "\r" not in cleaned
    assert "   " not in cleaned
    assert "\n\n\n" not in cleaned


def test_split_into_clauses_by_numbering():
    text = (
        "1. Termination. Either party may terminate this Agreement with notice.\n\n"
        "2. Confidentiality. Both parties shall keep information confidential."
    )
    clauses = split_into_clauses(text, min_length=10)
    assert len(clauses) == 2
    assert "Termination" in clauses[0]
    assert "Confidentiality" in clauses[1]


def test_split_into_clauses_fallback_on_paragraphs():
    text = "This is paragraph one with enough length to count.\n\nThis is paragraph two also long enough."
    clauses = split_into_clauses(text, min_length=10)
    assert len(clauses) == 2

def test_pdf_uses_ocr_fallback_for_scanned_page(tmp_path, monkeypatch):
    import fitz
    from app.ingestion import parser

    pdf_path = tmp_path / "scanned.pdf"

    document = fitz.open()
    document.new_page()
    document.save(pdf_path)
    document.close()

    monkeypatch.setattr(
        parser,
        "_ocr_pdf_page",
        lambda file_path, page_number, dpi=300:
            "OCR extracted contract text",
    )

    text = parser.extract_text_from_pdf(str(pdf_path))

    assert text == "OCR extracted contract text"
