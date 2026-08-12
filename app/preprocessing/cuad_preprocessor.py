"""
Week 1 module: CUAD dataset preprocessing.

Converts the nested CUAD/SQuAD-style JSON dataset into
flat JSONL records that can be used by downstream NLP
and transformer training pipelines.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_cuad(input_path: str | Path) -> dict[str, Any]:
    """
    Load and validate a CUAD JSON dataset.
    """

    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(
            f"CUAD dataset not found: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    if "data" not in dataset:
        raise ValueError(
            "Invalid CUAD dataset: missing top-level 'data' field."
        )

    if not isinstance(dataset["data"], list):
        raise ValueError(
            "Invalid CUAD dataset: 'data' must be a list."
        )

    return dataset


def flatten_cuad(
    dataset: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Flatten nested CUAD records.

    Output:
    One record per question / clause annotation.
    """

    records: list[dict[str, Any]] = []

    for contract in dataset.get("data", []):
        title = contract.get("title", "").strip()

        for paragraph in contract.get("paragraphs", []):
            context = paragraph.get(
                "context",
                "",
            ).strip()

            if not context:
                continue

            for qa in paragraph.get("qas", []):
                answers = qa.get("answers", []) or []

                answer_texts = []
                answer_starts = []

                for answer in answers:
                    answer_texts.append(
                        answer.get("text", "").strip()
                    )

                    answer_starts.append(
                        answer.get("answer_start", -1)
                    )

                record = {
                    "id": str(
                        qa.get("id", "")
                    ),
                    "title": title,
                    "context": context,
                    "question": qa.get(
                        "question",
                        "",
                    ).strip(),
                    "answers": {
                        "text": answer_texts,
                        "answer_start": answer_starts,
                    },
                    "is_impossible": qa.get(
                        "is_impossible",
                        len(answers) == 0,
                    ),
                }

                records.append(record)

    return records


def save_jsonl(
    records: list[dict[str, Any]],
    output_path: str | Path,
) -> None:
    """
    Save training records as JSON Lines.
    """

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
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


def preprocess_cuad(
    input_path: str | Path,
    output_path: str | Path,
) -> int:
    """
    Execute the complete CUAD preprocessing pipeline.

    Returns:
        Number of generated training records.
    """

    dataset = load_cuad(input_path)

    records = flatten_cuad(dataset)

    save_jsonl(
        records,
        output_path,
    )

    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Convert CUAD JSON into "
            "training-ready JSONL."
        )
    )

    parser.add_argument(
        "input",
        help="Path to raw CUAD JSON file",
    )

    parser.add_argument(
        "output",
        help="Path to processed JSONL file",
    )

    args = parser.parse_args()

    count = preprocess_cuad(
        args.input,
        args.output,
    )

    print(
        f"Successfully processed {count} "
        f"CUAD records."
    )

    print(
        f"Output saved to: {args.output}"
    )


if __name__ == "__main__":
    main()