"""
Day 1 module: text cleaning + clause segmentation helpers.
Contracts don't come as neat sentences -- this normalizes whitespace and
splits the document into clause-sized chunks for downstream NER/classification.
"""
from __future__ import annotations
import re
from typing import List


def clean_text(raw_text: str) -> str:
    """Collapse excess whitespace, normalize line breaks, strip page artifacts."""
    text = re.sub(r"\r\n?", "\n", raw_text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_clauses(text: str, min_length: int = 40) -> List[str]:
    """
    Naive clause splitter: legal docs usually number clauses like
    '1.', '1.1', 'Section 3:', etc. Falls back to paragraph splitting.
    Replace this with a smarter model-based segmenter later if needed.
    """
    clause_pattern = re.compile(
        r"(?=\n\s*(?:\d+\.\d*\s|\d+\)\s|\bSection\s+\d+\b|\bClause\s+\d+\b|\bARTICLE\s+[IVXLCDM]+\b))",
        re.IGNORECASE,
    )
    raw_splits = clause_pattern.split(text)

    clauses = []
    for chunk in raw_splits:
        chunk = chunk.strip()
        if len(chunk) >= min_length:
            clauses.append(chunk)

    # Fallback: if numbering wasn't detected, split on blank lines
    if len(clauses) <= 1:
        clauses = [p.strip() for p in text.split("\n\n") if len(p.strip()) >= min_length]

    return clauses