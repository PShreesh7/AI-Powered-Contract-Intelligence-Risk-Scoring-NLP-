"""Reusable contract-analysis application service.

The FastAPI layer should be responsible for HTTP concerns only.
This service contains the reusable document-analysis workflow:

    raw document
        -> text extraction
        -> cleaning
        -> NER
        -> clause segmentation
        -> clause classification
        -> risk analysis
        -> DocumentAnalysis
"""

from __future__ import annotations

import uuid

from typing import Any

from app.ingestion.parser import (
    extract_text,
)

from app.models.schemas import (
    DocumentAnalysis,
)

from app.risk.risk_flagger import (
    flag_risks,
)

from app.utils.text_utils import (
    clean_text,
    split_into_clauses,
)


class ContractAnalysisService:
    """Run the complete NLP contract-analysis pipeline."""

    def __init__(
        self,
        entity_extractor: Any,
        clause_classifier: Any,
    ) -> None:
        self.entity_extractor = (
            entity_extractor
        )

        self.clause_classifier = (
            clause_classifier
        )

    @staticmethod
    def build_offsets(
        text: str,
        clauses: list[str],
    ) -> list[
        tuple[int, int]
    ]:
        """Locate clause character offsets in normalized text."""

        offsets = []

        cursor = 0

        for clause in clauses:

            start = text.find(
                clause,
                cursor,
            )

            if start == -1:
                start = text.find(
                    clause
                )

            if start == -1:
                start = cursor

            end = (
                start
                + len(clause)
            )

            offsets.append(
                (
                    start,
                    end,
                )
            )

            cursor = end

        return offsets

    def analyze_text(
        self,
        raw_text: str,
        *,
        filename: str,
    ) -> DocumentAnalysis:
        """Analyze already-extracted contract text."""

        text = clean_text(
            raw_text
        )

        if not text:
            raise ValueError(
                "Document contains no "
                "readable text."
            )

        entities = (
            self.entity_extractor
            .extract(
                text
            )
        )

        clause_texts = (
            split_into_clauses(
                text
            )
        )

        if not clause_texts:
            raise ValueError(
                "No clause-sized text "
                "segments could be extracted "
                "from the document."
            )

        offsets = self.build_offsets(
            text,
            clause_texts,
        )

        clauses = (
            self.clause_classifier
            .classify(
                clause_texts,
                offsets,
            )
        )

        risk_flags = (
            flag_risks(
                clauses
            )
        )

        return DocumentAnalysis(
            document_id=str(
                uuid.uuid4()
            ),
            filename=filename,
            raw_text_length=len(
                text
            ),
            entities=entities,
            clauses=clauses,
            risk_flags=risk_flags,
        )

    def analyze_file(
        self,
        path: str,
        *,
        filename: str,
    ) -> DocumentAnalysis:
        """Extract and analyze a supported contract document."""

        raw_text = extract_text(
            path
        )

        return self.analyze_text(
            raw_text,
            filename=filename,
        )