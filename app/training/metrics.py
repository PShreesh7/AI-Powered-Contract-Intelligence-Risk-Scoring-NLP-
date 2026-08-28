"""Multiclass classification metrics."""

from __future__ import annotations


def multiclass_metrics(
    y_true,
    y_pred,
    num_labels,
):

    truth = list(
        y_true
    )

    predicted = list(
        y_pred
    )

    if (
        len(truth)
        != len(predicted)
    ):
        raise ValueError(
            "y_true and y_pred "
            "must have same length"
        )

    total = len(
        truth
    )

    correct = sum(
        int(a == b)
        for a, b
        in zip(
            truth,
            predicted,
        )
    )

    per_class = {}

    precisions = []
    recalls = []
    f1_scores = []

    for label_id in range(
        num_labels
    ):

        tp = sum(
            1
            for a, b
            in zip(
                truth,
                predicted,
            )
            if (
                a == label_id
                and b == label_id
            )
        )

        fp = sum(
            1
            for a, b
            in zip(
                truth,
                predicted,
            )
            if (
                a != label_id
                and b == label_id
            )
        )

        fn = sum(
            1
            for a, b
            in zip(
                truth,
                predicted,
            )
            if (
                a == label_id
                and b != label_id
            )
        )

        support = sum(
            1
            for value in truth
            if value == label_id
        )

        precision = (
            tp / (tp + fp)
            if tp + fp
            else 0.0
        )

        recall = (
            tp / (tp + fn)
            if tp + fn
            else 0.0
        )

        f1 = (
            (
                2
                * precision
                * recall
                / (
                    precision
                    + recall
                )
            )
            if (
                precision
                + recall
            )
            else 0.0
        )

        precisions.append(
            precision
        )

        recalls.append(
            recall
        )

        f1_scores.append(
            f1
        )

        per_class[
            str(label_id)
        ] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
        }

    divisor = (
        num_labels
        or 1
    )

    return {
        "accuracy": (
            correct / total
            if total
            else 0.0
        ),
        "macro_precision": (
            sum(precisions)
            / divisor
        ),
        "macro_recall": (
            sum(recalls)
            / divisor
        ),
        "macro_f1": (
            sum(f1_scores)
            / divisor
        ),
        "per_class": (
            per_class
        ),
        "samples": total,
    }


def trainer_metrics(
    eval_prediction,
):

    import numpy as np

    logits, labels = (
        eval_prediction
    )

    predictions = np.argmax(
        logits,
        axis=-1,
    )

    num_labels = (
        logits.shape[-1]
    )

    metrics = (
        multiclass_metrics(
            labels.tolist(),
            predictions.tolist(),
            num_labels,
        )
    )

    return {
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
    }