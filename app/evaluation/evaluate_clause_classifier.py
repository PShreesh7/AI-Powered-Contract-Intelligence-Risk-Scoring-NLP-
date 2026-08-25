from __future__ import annotations

import argparse
import json

from pathlib import Path

from app.preprocessing.clause_dataset import (
    load_jsonl,
)

from app.training.metrics import (
    multiclass_metrics,
)


def build_confusion_matrix(
    y_true,
    y_pred,
    num_labels,
):

    matrix = [
        [
            0
            for _ in range(
                num_labels
            )
        ]
        for _ in range(
            num_labels
        )
    ]

    for truth, pred in zip(
        y_true,
        y_pred,
    ):

        matrix[
            truth
        ][
            pred
        ] += 1

    return matrix


def evaluate_clause_classifier(
    model_dir,
    test_file,
    *,
    output_file=None,
    batch_size=16,
    max_length=256,
):

    import torch

    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
    )

    model_dir = Path(
        model_dir
    )

    records = load_jsonl(
        test_file
    )

    if not records:
        raise ValueError(
            "Test split is empty."
        )

    tokenizer = (
        AutoTokenizer
        .from_pretrained(
            str(model_dir)
        )
    )

    model = (
        AutoModelForSequenceClassification
        .from_pretrained(
            str(model_dir)
        )
    )

    model.eval()

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    model.to(
        device
    )

    y_true = []
    y_pred = []

    with torch.no_grad():

        for start in range(
            0,
            len(records),
            batch_size,
        ):

            batch = records[
                start:
                start + batch_size
            ]

            texts = [
                record["text"]
                for record
                in batch
            ]

            encoded = (
                tokenizer(
                    texts,
                    truncation=True,
                    padding=True,
                    max_length=(
                        max_length
                    ),
                    return_tensors="pt",
                )
            )

            encoded = {
                key: value.to(
                    device
                )
                for key, value
                in encoded.items()
            }

            logits = (
                model(
                    **encoded
                ).logits
            )

            predictions = (
                torch.argmax(
                    logits,
                    dim=-1,
                )
                .cpu()
                .tolist()
            )

            y_pred.extend(
                predictions
            )

            y_true.extend(
                int(
                    record[
                        "label_id"
                    ]
                )
                for record
                in batch
            )

    num_labels = int(
        model.config.num_labels
    )

    metrics = (
        multiclass_metrics(
            y_true,
            y_pred,
            num_labels,
        )
    )

    matrix = (
        build_confusion_matrix(
            y_true,
            y_pred,
            num_labels,
        )
    )

    id2label = {
        int(key): value
        for key, value
        in dict(
            model.config.id2label
        ).items()
    }

    per_class_named = {}

    for (
        label_id,
        class_metrics,
    ) in (
        metrics[
            "per_class"
        ].items()
    ):

        numeric_id = int(
            label_id
        )

        label_name = (
            id2label.get(
                numeric_id,
                str(numeric_id),
            )
        )

        per_class_named[
            label_name
        ] = class_metrics

    report = {
        "model_dir": str(
            model_dir
        ),
        "test_examples": (
            len(records)
        ),
        "accuracy": (
            metrics[
                "accuracy"
            ]
        ),
        "macro_precision": (
            metrics[
                "macro_precision"
            ]
        ),
        "macro_recall": (
            metrics[
                "macro_recall"
            ]
        ),
        "macro_f1": (
            metrics[
                "macro_f1"
            ]
        ),
        "per_class": (
            per_class_named
        ),
        "confusion_matrix": (
            matrix
        ),
        "labels": [
            id2label.get(
                index,
                str(index),
            )
            for index
            in range(
                num_labels
            )
        ],
    }

    if output_file:

        path = Path(
            output_file
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                report,
                file,
                indent=2,
            )

    return report


def main():

    parser = (
        argparse.ArgumentParser()
    )

    parser.add_argument(
        "--model-dir",
        required=True,
    )

    parser.add_argument(
        "--test-file",
        required=True,
    )

    parser.add_argument(
        "--output-file",
        default=(
            "outputs/"
            "clause_classifier_"
            "test_report.json"
        ),
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
    )

    parser.add_argument(
        "--max-length",
        type=int,
        default=256,
    )

    args = parser.parse_args()

    report = (
        evaluate_clause_classifier(
            args.model_dir,
            args.test_file,
            output_file=(
                args.output_file
            ),
            batch_size=(
                args.batch_size
            ),
            max_length=(
                args.max_length
            ),
        )
    )

    print(
        json.dumps(
            report,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()