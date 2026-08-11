"""
Day 1 module: document ingestion.
Extracts raw text from PDF and DOCX contract files.
"""
from __future__ import annotations
import os
import fitz  # PyMuPDF
import docx  # python-docx


class UnsupportedFileTypeError(Exception):
    pass


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from every page of a PDF using PyMuPDF."""
    text_chunks = []
    with fitz.open(file_path) as doc:
        for page in doc:
            text_chunks.append(page.get_text())
    return "\n".join(text_chunks)


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a Word document, including table cells."""
    document = docx.Document(file_path)
    parts = [p.text for p in document.paragraphs if p.text.strip()]

    for table in document.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells)
            if row_text.strip():
                parts.append(row_text)

    return "\n".join(parts)


def extract_text(file_path: str) -> str:
    """Dispatch to the right extractor based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(file_path)
    else:
        raise UnsupportedFileTypeError(f"Unsupported file type: {ext}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python parser.py <path_to_contract>")
        sys.exit(1)
    print(extract_text(sys.argv[1])[:2000])
