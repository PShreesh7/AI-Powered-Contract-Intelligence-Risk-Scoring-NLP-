"""Build clause classification dataset from CUAD annotations."""

from __future__ import annotations

import argparse
import json
import re

from collections import Counter
from pathlib import Path
from typing import Any, Iterable


LABEL_CLEAN_RE = re.compile(
    r"[^A-Za-z0-9]+"
)


def normalize_clause_label(
    value: str,
) -> str:

    label = (
        LABEL_CLEAN_RE
        .sub(
            "_",
            value.strip(),
        )
        .strip("_")
        .upper()
    )

    label = re.sub(
        r"_+",
        "_",
        label,
    )

    return (
        label
        or "UNKNOWN"
    )


def derive_clause_label(
    record: dict[str, Any],
) -> str:

    record_id = str(
        record.get(
            "id",
            "",
        )
    )

    if "__" in record_id:

        suffix = (
            record_id
            .rsplit(
                "__",
                1,
            )[-1]
            .strip()
        )

        if suffix:
            return (
                normalize_clause_label(
                    suffix
                )
            )

    question = str(
        record.get(
            "question",
            "",
        )
    ).strip()

    if question:
        return (
            normalize_clause_label(
                question
            )
        )

    return "UNKNOWN"


def load_jsonl(
    path: str | Path,
) -> list[dict[str, Any]]:

    records = []

    with Path(path).open(
        "r",
        encoding="utf-8",
    ) as file:

        for line_number, line in enumerate(
            file,
            start=1,
        ):

            if not line.strip():
                continue

            try:
                records.append(
                    json.loads(
                        line
                    )
                )

            except json.JSONDecodeError as exc:

                raise ValueError(
                    f"Invalid JSONL "
                    f"at line "
                    f"{line_number}"
                ) from exc

    return records


def build_clause_records(
    flattened_records: Iterable[
        dict[str, Any]
    ],
) -> list[dict[str, Any]]:

    examples = []

    seen = set()

    for record in (
        flattened_records
    ):

        if record.get(
            "is_impossible"
        ):
            continue

        label = (
            derive_clause_label(
                record
            )
        )

        answers = (
            record.get(
                "answers",
                {},
            )
        )

        texts = (
            answers.get(
                "text",
                [],
            )
            or []
        )

        starts = (
            answers.get(
                "answer_start",
                [],
            )
            or []
        )

        if (
            len(texts)
            != len(starts)
        ):
            raise ValueError(
                "Answer text/start "
                "count mismatch."
            )

        for (
            answer_index,
            (text, start),
        ) in enumerate(
            zip(
                texts,
                starts,
            )
        ):

            if (
                not isinstance(
                    text,
                    str,
                )
                or not text.strip()
            ):
                continue

            if (
                not isinstance(
                    start,
                    int,
                )
                or start < 0
            ):
                continue

            key = (
                str(
                    record.get(
                        "title",
                        "",
                    )
                ),
                label,
                start,
                text,
            )

            if key in seen:
                continue

            seen.add(
                key
            )

            examples.append(
                {
                    "id": (
                        f"{record.get('id', '')}"
                        f"::{answer_index}"
                    ),
                    "source_id": str(
                        record.get(
                            "id",
                            "",
                        )
                    ),
                    "title": str(
                        record.get(
                            "title",
                            "",
                        )
                    ),
                    "label": label,
                    "text": text,
                    "start_char": start,
                    "end_char": (
                        start
                        + len(text)
                    ),
                }
            )

    return examples


def save_jsonl(
    records,
    path,
):

    output = Path(
        path
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output.open(
        "w",
        encoding="utf-8",
    ) as file:

        for record in records:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )


def label_distribution(
    records,
):

    counts = Counter(
        record["label"]
        for record in records
    )

    return dict(
        sorted(
            counts.items()
        )
    )


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "input"
    )

    parser.add_argument(
        "output"
    )

    args = parser.parse_args()

    records = load_jsonl(
        args.input
    )

    examples = (
        build_clause_records(
            records
        )
    )

    save_jsonl(
        examples,
        args.output,
    )

    distribution = (
        label_distribution(
            examples
        )
    )

    print(
        f"Created "
        f"{len(examples)} "
        f"clause examples."
    )

    print(
        f"Detected "
        f"{len(distribution)} "
        f"clause categories."
    )

    for label, count in (
        distribution.items()
    ):

        print(
            f"{label}: {count}"
        )


if __name__ == "__main__":
    main()