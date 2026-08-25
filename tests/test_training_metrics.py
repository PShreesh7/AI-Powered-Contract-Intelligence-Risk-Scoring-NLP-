from app.training.metrics import (
    multiclass_metrics,
)


def test_perfect_predictions():

    metrics = (
        multiclass_metrics(
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            2,
        )
    )

    assert (
        metrics["accuracy"]
        == 1.0
    )

    assert (
        metrics[
            "macro_precision"
        ]
        == 1.0
    )

    assert (
        metrics[
            "macro_recall"
        ]
        == 1.0
    )

    assert (
        metrics["macro_f1"]
        == 1.0
    )


def test_missing_prediction():

    metrics = (
        multiclass_metrics(
            [0, 1],
            [0, 0],
            2,
        )
    )

    assert (
        metrics["accuracy"]
        == 0.5
    )

    assert (
        metrics[
            "per_class"
        ]["1"]["precision"]
        == 0.0
    )

    assert (
        metrics[
            "per_class"
        ]["1"]["recall"]
        == 0.0
    )