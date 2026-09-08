from app.models.schemas import ClauseSegment, DocumentAnalysis, ExtractedEntity, RiskFlag
from app.reports.pdf_report import generate_pdf_report


def test_generate_pdf_report_with_flags():
    analysis = DocumentAnalysis(
        document_id="doc-test-1234",
        filename="Test_Agreement.pdf",
        raw_text_length=1500,
        entities=[
            ExtractedEntity(label="PARTY", text="Acme Corp", start_char=0, end_char=9, confidence=1.0),
            ExtractedEntity(label="DATE", text="January 1, 2024", start_char=15, end_char=30, confidence=1.0),
            ExtractedEntity(label="JURISDICTION", text="Delaware", start_char=40, end_char=48, confidence=0.8),
        ],
        clauses=[
            ClauseSegment(
                clause_id="c1",
                text="Either party may terminate at sole discretion.",
                clause_type="termination",
                confidence=0.92,
                start_char=0,
                end_char=47,
            ),
        ],
        risk_flags=[
            RiskFlag(
                clause_id="c1",
                risk_level="medium",
                reason="Grants one-sided discretionary power.",
                suggestion="Require mutual agreement and notice.",
            )
        ],
    )

    pdf_bytes = generate_pdf_report(analysis)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF-")


def test_generate_pdf_report_no_flags():
    analysis = DocumentAnalysis(
        document_id="doc-clean-1234",
        filename="Clean_Agreement.docx",
        raw_text_length=800,
        entities=[],
        clauses=[
            ClauseSegment(
                clause_id="c1",
                text="This agreement is governed by the laws of California.",
                clause_type="governing law",
                confidence=0.98,
                start_char=0,
                end_char=53,
            ),
        ],
        risk_flags=[],
    )

    pdf_bytes = generate_pdf_report(analysis)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF-")
