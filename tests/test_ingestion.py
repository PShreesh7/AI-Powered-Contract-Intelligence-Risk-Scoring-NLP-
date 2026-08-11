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
