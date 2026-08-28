from app.preprocessing.clause_dataset import (
    build_clause_records,
    derive_clause_label,
    label_distribution,
    normalize_clause_label,
)


def test_normalize_label():

    assert (
        normalize_clause_label(
            "Governing Law"
        )
        == "GOVERNING_LAW"
    )

    assert (
        normalize_clause_label(
            "IP Ownership / Assignment"
        )
        == "IP_OWNERSHIP_ASSIGNMENT"
    )


def test_derive_label():

    record = {
        "id": (
            "contract__"
            "Change Of Control"
        ),
        "question": (
            "Some question"
        ),
    }

    assert (
        derive_clause_label(
            record
        )
        == "CHANGE_OF_CONTROL"
    )


def test_positive_answers_only():

    records = [
        {
            "id": (
                "contract__"
                "Governing Law"
            ),
            "title": "contract",
            "question": (
                "What is governing law?"
            ),
            "answers": {
                "text": [
                    "laws of Delaware"
                ],
                "answer_start": [
                    25
                ],
            },
            "is_impossible": False,
        },
        {
            "id": (
                "contract__"
                "Non-Compete"
            ),
            "title": "contract",
            "question": (
                "Non compete?"
            ),
            "answers": {
                "text": [],
                "answer_start": [],
            },
            "is_impossible": True,
        },
    ]

    examples = (
        build_clause_records(
            records
        )
    )

    assert len(
        examples
    ) == 1

    assert (
        examples[0]["label"]
        == "GOVERNING_LAW"
    )

    assert (
        examples[0]["text"]
        == "laws of Delaware"
    )

    assert (
        label_distribution(
            examples
        )
        == {
            "GOVERNING_LAW": 1
        }
    )


def test_duplicate_removed():

    record = {
        "id": (
            "contract__Termination"
        ),
        "title": "contract",
        "question": (
            "Termination?"
        ),
        "answers": {
            "text": [
                (
                    "Either party "
                    "may terminate"
                ),
                (
                    "Either party "
                    "may terminate"
                ),
            ],
            "answer_start": [
                10,
                10,
            ],
        },
        "is_impossible": False,
    }

    examples = (
        build_clause_records(
            [record]
        )
    )

    assert len(
        examples
    ) == 1