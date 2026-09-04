import pytest

from app.models.schemas import (
    ClauseSegment,
    ExtractedEntity,
)

from app.services.contract_analysis import (
    ContractAnalysisService,
)


class FakeEntityExtractor:

    def extract(
        self,
        text,
    ):
        return [
            ExtractedEntity(
                label="PARTY",
                text="Acme Corporation",
                start_char=0,
                end_char=16,
                confidence=1.0,
            )
        ]


class FakeClauseClassifier:

    def __init__(
        self,
    ):
        self.calls = []

    def classify(
        self,
        clause_texts,
        offsets,
    ):
        self.calls.append(
            (
                clause_texts,
                offsets,
            )
        )

        results = []

        for index, (
            text,
            offset,
        ) in enumerate(
            zip(
                clause_texts,
                offsets,
            )
        ):
            results.append(
                ClauseSegment(
                    clause_id=(
                        f"clause-{index}"
                    ),
                    text=text,
                    clause_type=(
                        "termination"
                    ),
                    confidence=0.91,
                    needs_review=False,
                    start_char=(
                        offset[0]
                    ),
                    end_char=(
                        offset[1]
                    ),
                )
            )

        return results


def make_service():

    return ContractAnalysisService(
        entity_extractor=(
            FakeEntityExtractor()
        ),
        clause_classifier=(
            FakeClauseClassifier()
        ),
    )


def test_analyze_text_builds_document_analysis():

    service = make_service()

    raw_text = (
        "Section 1 Termination\n"
        "Either party may terminate "
        "this agreement after providing "
        "thirty days written notice."
    )

    analysis = service.analyze_text(
        raw_text,
        filename="contract.pdf",
    )

    assert (
        analysis.filename
        == "contract.pdf"
    )

    assert (
        analysis.raw_text_length
        > 0
    )

    assert (
        len(
            analysis.entities
        )
        == 1
    )

    assert (
        len(
            analysis.clauses
        )
        == 1
    )

    assert (
        analysis.clauses[0]
        .clause_type
        == "termination"
    )


def test_build_offsets_handles_repeated_text():

    text = (
        "alpha clause "
        "alpha clause"
    )

    offsets = (
        ContractAnalysisService
        .build_offsets(
            text,
            [
                "alpha clause",
                "alpha clause",
            ],
        )
    )

    assert offsets == [
        (
            0,
            12,
        ),
        (
            13,
            25,
        ),
    ]


def test_empty_document_is_rejected():

    service = make_service()

    with pytest.raises(
        ValueError,
        match="readable text",
    ):
        service.analyze_text(
            "   ",
            filename=(
                "empty.pdf"
            ),
        )