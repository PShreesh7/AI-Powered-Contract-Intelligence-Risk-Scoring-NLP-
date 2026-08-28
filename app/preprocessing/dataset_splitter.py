"""Create contract-level train, validation and test splits."""

from __future__ import annotations

import argparse
import json
import random

from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from app.preprocessing.clause_dataset import (
    load_jsonl,
    save_jsonl,
)


def build_label_mapping(
    records: Iterable[
        dict[str, Any]
    ],
):

    labels = sorted(
        {
            str(
                record["label"]
            )
            for record
            in records
        }
    )

    label2id = {
        label: index
        for index, label
        in enumerate(labels)
    }

    id2label = {
        str(index): label
        for label, index
        in label2id.items()
    }

    return {
        "label2id": label2id,
        "id2label": id2label,
    }


def _split_counts(
    n_groups,
    train_ratio,
    val_ratio,
):

    if n_groups <= 0:
        return 0, 0, 0

    if n_groups == 1:
        return 1, 0, 0

    if n_groups == 2:
        return 1, 1, 0

    n_train = max(
        1,
        round(
            n_groups
            * train_ratio
        ),
    )

    n_val = max(
        1,
        round(
            n_groups
            * val_ratio
        ),
    )

    if (
        n_train
        + n_val
        >= n_groups
    ):
        n_train = max(
            1,
            n_groups - 2,
        )

        n_val = 1

    n_test = (
        n_groups
        - n_train
        - n_val
    )

    return (
        n_train,
        n_val,
        n_test,
    )


def split_by_contract(
    records,
    *,
    train_ratio=0.70,
    val_ratio=0.15,
    seed=42,
):

    if not (
        0 < train_ratio < 1
    ):
        raise ValueError(
            "Invalid train ratio"
        )

    if not (
        0 <= val_ratio < 1
    ):
        raise ValueError(
            "Invalid validation ratio"
        )

    if (
        train_ratio
        + val_ratio
        >= 1
    ):
        raise ValueError(
            "Train + validation "
            "ratio must be < 1"
        )

    groups = defaultdict(
        list
    )

    for record in records:

        title = str(
            record.get(
                "title",
                "",
            )
        ).strip()

        if not title:

            title = (
                "__unknown__::"
                + str(
                    record.get(
                        "source_id",
                        record.get(
                            "id",
                            "",
                        ),
                    )
                )
            )

        groups[
            title
        ].append(
            record
        )

    titles = sorted(
        groups
    )

    random.Random(
        seed
    ).shuffle(
        titles
    )

    (
        n_train,
        n_val,
        _,
    ) = _split_counts(
        len(titles),
        train_ratio,
        val_ratio,
    )

    train_titles = set(
        titles[:n_train]
    )

    val_titles = set(
        titles[
            n_train:
            n_train + n_val
        ]
    )

    split_records = {
        "train": [],
        "validation": [],
        "test": [],
    }

    for title in titles:

        if title in train_titles:
            target = "train"

        elif title in val_titles:
            target = (
                "validation"
            )

        else:
            target = "test"

        split_records[
            target
        ].extend(
            groups[title]
        )

    for name in split_records:

        split_records[
            name
        ].sort(
            key=lambda record:
            str(
                record.get(
                    "id",
                    "",
                )
            )
        )

    return split_records


def attach_label_ids(
    records,
    label2id,
):

    output = []

    for record in records:

        item = dict(
            record
        )

        item["label_id"] = (
            label2id[
                str(
                    record["label"]
                )
            ]
        )

        output.append(
            item
        )

    return output


def save_splits(
    splits,
    label_mapping,
    output_dir,
):

    output = Path(
        output_dir
    )

    output.mkdir(
        parents=True,
        exist_ok=True,
    )

    label2id = (
        label_mapping[
            "label2id"
        ]
    )

    for (
        split_name,
        records,
    ) in splits.items():

        save_jsonl(
            attach_label_ids(
                records,
                label2id,
            ),
            output
            / f"{split_name}.jsonl",
        )

    with (
        output / "labels.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            label_mapping,
            file,
            indent=2,
        )


def main():

    parser = (
        argparse.ArgumentParser()
    )

    parser.add_argument(
        "input"
    )

    parser.add_argument(
        "output_dir"
    )

    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.70,
    )

    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.15,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )

    args = parser.parse_args()

    records = load_jsonl(
        args.input
    )

    mapping = (
        build_label_mapping(
            records
        )
    )

    splits = split_by_contract(
        records,
        train_ratio=(
            args.train_ratio
        ),
        val_ratio=(
            args.val_ratio
        ),
        seed=args.seed,
    )

    save_splits(
        splits,
        mapping,
        args.output_dir,
    )

    for name, items in (
        splits.items()
    ):

        print(
            f"{name}: "
            f"{len(items)} "
            f"examples"
        )


if __name__ == "__main__":
    main()