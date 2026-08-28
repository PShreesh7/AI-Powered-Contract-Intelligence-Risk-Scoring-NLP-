import pytest

from app.clauses.clause_classifier import (
    ClauseClassifier,
    display_clause_label,
)


def test_display_label():

    assert (
        display_clause_label(
            "GOVERNING_LAW"
        )
        == "governing law"
    )

    assert (
        display_clause_label(
            "Non-Compete"
        )
        == "non-compete"
    )


def test_low_confidence():

    classifier = (
        ClauseClassifier
        .__new__(
            ClauseClassifier
        )
    )

    classifier.mode = "test"

    classifier.confidence_threshold = (
        0.60
    )

    classifier._predict = (
        lambda _: (
            "GOVERNING_LAW",
            0.42,
        )
    )

    result = (
        classifier.classify(
            [
                "Governed by Delaware."
            ],
            [
                (0, 21)
            ],
        )[0]
    )

    assert (
        result.clause_type
        == "governing law"
    )

    assert (
        result.confidence
        == 0.42
    )

    assert (
        result.needs_review
        is True
    )


def test_high_confidence():

    classifier = (
        ClauseClassifier
        .__new__(
            ClauseClassifier
        )
    )

    classifier.mode = "test"

    classifier.confidence_threshold = (
        0.50
    )

    classifier._predict = (
        lambda _: (
            "TERMINATION_FOR_CONVENIENCE",
            0.91,
        )
    )

    result = (
        classifier.classify(
            [
                (
                    "Either party "
                    "may terminate."
                )
            ],
            [
                (0, 27)
            ],
        )[0]
    )

    assert (
        result.clause_type
        == (
            "termination "
            "for convenience"
        )
    )

    assert (
        result.needs_review
        is False
    )


def test_offset_mismatch():

    classifier = (
        ClauseClassifier
        .__new__(
            ClauseClassifier
        )
    )

    classifier.confidence_threshold = (
        0.50
    )

    with pytest.raises(
        ValueError
    ):

        classifier.classify(
            [
                "one clause"
            ],
            [],
        )