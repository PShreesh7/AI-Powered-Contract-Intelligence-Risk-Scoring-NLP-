from app.evaluation.evaluate_clause_classifier import (
    build_confusion_matrix,
)


def test_confusion_matrix():

    matrix = (
        build_confusion_matrix(
            y_true=[
                0,
                0,
                1,
                1,
                2,
            ],
            y_pred=[
                0,
                1,
                1,
                1,
                0,
            ],
            num_labels=3,
        )
    )

    assert matrix == [
        [1, 1, 0],
        [0, 2, 0],
        [1, 0, 0],
    ]