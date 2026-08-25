from app.preprocessing.dataset_splitter import (
    attach_label_ids,
    build_label_mapping,
    split_by_contract,
)


def make_records():

    rows = []

    for contract_number in range(
        10
    ):

        for label in (
            "TERMINATION",
            "GOVERNING_LAW",
        ):

            rows.append(
                {
                    "id": (
                        f"{contract_number}"
                        f"-{label}"
                    ),
                    "source_id": (
                        str(
                            contract_number
                        )
                    ),
                    "title": (
                        f"contract-"
                        f"{contract_number}"
                    ),
                    "label": label,
                    "text": (
                        f"sample {label}"
                    ),
                }
            )

    return rows


def test_no_contract_leakage():

    splits = split_by_contract(
        make_records(),
        seed=7,
    )

    title_sets = {
        name: {
            record["title"]
            for record
            in records
        }
        for name, records
        in splits.items()
    }

    assert (
        title_sets["train"]
        .isdisjoint(
            title_sets[
                "validation"
            ]
        )
    )

    assert (
        title_sets["train"]
        .isdisjoint(
            title_sets[
                "test"
            ]
        )
    )


def test_deterministic():

    first = split_by_contract(
        make_records(),
        seed=42,
    )

    second = split_by_contract(
        make_records(),
        seed=42,
    )

    assert (
        first
        == second
    )


def test_label_mapping():

    rows = make_records()

    mapping = (
        build_label_mapping(
            rows
        )
    )

    assert (
        mapping["label2id"]
        == {
            "GOVERNING_LAW": 0,
            "TERMINATION": 1,
        }
    )

    with_ids = attach_label_ids(
        rows[:2],
        mapping["label2id"],
    )

    assert all(
        "label_id" in row
        for row
        in with_ids
    )