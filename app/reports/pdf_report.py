"""
Week 3 module: PDF report export.
Takes a DocumentAnalysis (entities, clauses, risk flags) and produces a
clean, downloadable PDF summary.
"""
from __future__ import annotations
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

from app.models.schemas import DocumentAnalysis

RISK_COLORS = {
    "high": colors.HexColor("#A63D40"),
    "medium": colors.HexColor("#B8860B"),
    "low": colors.HexColor("#2F6844"),
}


def generate_pdf_report(analysis: DocumentAnalysis) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.8 * inch,
        bottomMargin=0.8 * inch,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=18, spaceAfter=4)
    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=10, textColor=colors.grey, spaceAfter=18)
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, spaceBefore=16, spaceAfter=8)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=14, spaceAfter=6)
    small_style = ParagraphStyle("Small", parent=styles["Normal"], fontSize=9, textColor=colors.grey)

    story = []
    story.append(Paragraph("Contract Risk Report", title_style))
    story.append(Paragraph(f"Source document: {analysis.filename}", subtitle_style))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#C9C4B8")))

    story.append(Paragraph("Summary", h2_style))
    high = sum(1 for f in analysis.risk_flags if f.risk_level == "high")
    medium = sum(1 for f in analysis.risk_flags if f.risk_level == "medium")
    low = sum(1 for f in analysis.risk_flags if f.risk_level == "low")

    summary_data = [
        ["Clauses reviewed", str(len(analysis.clauses))],
        ["Entities found", str(len(analysis.entities))],
        ["High-risk flags", str(high)],
        ["Medium-risk flags", str(medium)],
        ["Low-risk flags", str(low)],
    ]
    summary_table = Table(summary_data, colWidths=[220, 100])
    summary_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#E0DED4")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#45526E")),
    ]))
    story.append(summary_table)

    story.append(Paragraph("Parties &amp; Key Facts", h2_style))
    by_label: dict[str, set[str]] = {}
    for e in analysis.entities:
        by_label.setdefault(e.label, set()).add(e.text)

    if by_label:
        for label, values in by_label.items():
            story.append(Paragraph(f"<b>{label}:</b> {', '.join(sorted(values))}", body_style))
    else:
        story.append(Paragraph("No entities detected.", body_style))

    story.append(Paragraph("Flagged Clauses", h2_style))
    clause_by_id = {c.clause_id: c for c in analysis.clauses}

    if not analysis.risk_flags:
        story.append(Paragraph("No risk flags were raised for this document.", body_style))
    else:
        for flag in analysis.risk_flags:
            clause = clause_by_id.get(flag.clause_id)
            color = RISK_COLORS.get(flag.risk_level, colors.grey)
            level_style = ParagraphStyle(
                "Level", parent=body_style, textColor=color, fontName="Helvetica-Bold"
            )
            story.append(Paragraph(f"{flag.risk_level.upper()} RISK", level_style))
            if clause:
                story.append(Paragraph(f"<i>Clause type: {clause.clause_type}</i>", small_style))
                preview = clause.text[:280] + ("..." if len(clause.text) > 280 else "")
                story.append(Paragraph(preview, body_style))
            story.append(Paragraph(f"Reason: {flag.reason}", body_style))
            if flag.suggestion:
                story.append(Paragraph(f"Suggestion: {flag.suggestion}", body_style))
            story.append(Spacer(1, 10))

    story.append(Paragraph("All Clause Types Detected", h2_style))
    type_counts: dict[str, int] = {}
    for c in analysis.clauses:
        type_counts[c.clause_type] = type_counts.get(c.clause_type, 0) + 1
    type_data = [[t, str(n)] for t, n in sorted(type_counts.items())]
    if type_data:
        type_table = Table([["Clause type", "Count"]] + type_data, colWidths=[300, 60])
        type_table.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0DED4")),
        ]))
        story.append(type_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.read()