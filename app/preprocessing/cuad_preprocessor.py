from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class CUADSpanValidationError(ValueError):
    """Raised when an annotated answer does not match its context span."""


def load_cuad(input_path: str | Path) -> dict[str, Any]:
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


def _validate_answer_span(
    context: str,
    text: str,
    start: int,
) -> None:

    if not isinstance(start, int) or start < 0:
        raise CUADSpanValidationError(
            f"Invalid answer_start={start!r}."
        )

    end = start + len(text)

    if end > len(context):
        raise CUADSpanValidationError(
            f"Answer span [{start}:{end}] "
            f"exceeds context length {len(context)}."
        )

    observed = context[start:end]

    if observed != text:
        raise CUADSpanValidationError(
            "CUAD answer span mismatch: "
            f"expected {text!r} at "
            f"[{start}:{end}], "
            f"found {observed!r}."
        )


def flatten_cuad(
    dataset: dict[str, Any],
) -> list[dict[str, Any]]:

    records: list[dict[str, Any]] = []

    for contract in dataset.get("data", []):
        title = str(
            contract.get("title", "")
        ).strip()

        paragraphs = (
            contract.get("paragraphs", [])
            or []
        )

        for paragraph in paragraphs:

            # IMPORTANT:
            # Do not use .strip() here because
            # answer_start is based on original context.
            context = paragraph.get(
                "context",
                "",
            )

            if (
                not isinstance(context, str)
                or not context.strip()
            ):
                continue

            for qa in (
                paragraph.get("qas", [])
                or []
            ):

                answers = (
                    qa.get("answers", [])
                    or []
                )

                answer_texts = []
                answer_starts = []

                for answer in answers:

                    answer_text = answer.get(
                        "text",
                        "",
                    )

                    answer_start = answer.get(
                        "answer_start",
                        -1,
                    )

                    if not isinstance(
                        answer_text,
                        str,
                    ):
                        answer_text = str(
                            answer_text
                        )

                    answer_texts.append(
                        answer_text
                    )

                    answer_starts.append(
                        answer_start
                    )

                records.append(
                    {
                        "id": str(
                            qa.get(
                                "id",
                                "",
                            )
                        ),
                        "title": title,
                        "context": context,
                        "question": str(
                            qa.get(
                                "question",
                                "",
                            )
                        ).strip(),
                        "answers": {
                            "text": (
                                answer_texts
                            ),
                            "answer_start": (
                                answer_starts
                            ),
                        },
                        "is_impossible": (
                            qa.get(
                                "is_impossible",
                                len(answers) == 0,
                            )
                        ),
                    }
                )

    return records


def validate_records(
    records: list[dict[str, Any]],
) -> dict[str, int]:

    positive_records = 0
    impossible_records = 0
    answer_spans = 0

    for record in records:

        context = record["context"]

        texts = (
            record
            .get("answers", {})
            .get("text", [])
        )

        starts = (
            record
            .get("answers", {})
            .get(
                "answer_start",
                [],
            )
        )

        if len(texts) != len(starts):
            raise CUADSpanValidationError(
                f"Record "
                f"{record.get('id', '<unknown>')} "
                "has unequal answer "
                "text/start counts."
            )

        if (
            record.get("is_impossible")
            or not texts
        ):
            impossible_records += 1
            continue

        positive_records += 1

        for text, start in zip(
            texts,
            starts,
        ):

            _validate_answer_span(
                context,
                text,
                start,
            )

            answer_spans += 1

    return {
        "records": len(records),
        "positive_records": (
            positive_records
        ),
        "impossible_records": (
            impossible_records
        ),
        "answer_spans": answer_spans,
    }


def save_jsonl(
    records: list[dict[str, Any]],
    output_path: str | Path,
) -> None:

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
    *,
    validate_spans: bool = True,
) -> int:

    dataset = load_cuad(
        input_path
    )

    records = flatten_cuad(
        dataset
    )

    if validate_spans:
        validate_records(
            records
        )

    save_jsonl(
        records,
        output_path,
    )

    return len(records)


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Convert CUAD JSON into "
            "validated training-ready JSONL."
        )
    )

    parser.add_argument(
        "input"
    )

    parser.add_argument(
        "output"
    )

    parser.add_argument(
        "--skip-span-validation",
        action="store_true",
    )

    args = parser.parse_args()

    dataset = load_cuad(
        args.input
    )

    records = flatten_cuad(
        dataset
    )

    stats = None

    if not args.skip_span_validation:
        stats = validate_records(
            records
        )

    save_jsonl(
        records,
        args.output,
    )

    print(
        f"Successfully processed "
        f"{len(records)} CUAD records."
    )

    if stats:
        print(
            f"Validated "
            f"{stats['answer_spans']} "
            f"answer spans across "
            f"{stats['positive_records']} "
            f"positive records."
        )

    print(
        f"Output saved to: "
        f"{args.output}"
    )


if __name__ == "__main__":
    main()