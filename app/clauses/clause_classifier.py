from __future__ import annotations

import os
import uuid

from app.models.schemas import (
    ClauseSegment,
)


ZERO_SHOT_LABELS = [
    "termination",
    "confidentiality",
    "indemnification",
    "limitation of liability",
    "governing law",
    "payment terms",
    "intellectual property",
    "force majeure",
    "non-compete",
    "dispute resolution",
]


def display_clause_label(
    label: str,
) -> str:

    return (
        label
        .strip()
        .replace(
            "_",
            " ",
        )
        .lower()
    )


class ClauseClassifier:

    def __init__(
        self,
        model_name_or_path=None,
        *,
        zero_shot_model_name=(
            "facebook/"
            "bart-large-mnli"
        ),
        confidence_threshold=0.50,
    ):

        self.confidence_threshold = (
            confidence_threshold
        )

        if model_name_or_path:

            import torch

            from transformers import (
                AutoModelForSequenceClassification,
                AutoTokenizer,
            )

            self.mode = (
                "fine_tuned"
            )

            self._torch = torch

            self.tokenizer = (
                AutoTokenizer
                .from_pretrained(
                    model_name_or_path
                )
            )

            self.model = (
                AutoModelForSequenceClassification
                .from_pretrained(
                    model_name_or_path
                )
            )

            self.model.eval()

            self.device = (
                torch.device(
                    "cuda"
                    if torch.cuda.is_available()
                    else "cpu"
                )
            )

            self.model.to(
                self.device
            )

        else:

            from transformers import (
                pipeline,
            )

            self.mode = (
                "zero_shot"
            )

            self.classifier = (
                pipeline(
                    (
                        "zero-shot-"
                        "classification"
                    ),
                    model=(
                        zero_shot_model_name
                    ),
                )
            )


    def _predict(
        self,
        clause_text,
    ):

        if (
            self.mode
            == "fine_tuned"
        ):

            encoded = (
                self.tokenizer(
                    clause_text,
                    truncation=True,
                    max_length=256,
                    return_tensors="pt",
                )
            )

            encoded = {
                key: value.to(
                    self.device
                )
                for key, value
                in encoded.items()
            }

            with (
                self._torch
                .no_grad()
            ):

                logits = (
                    self.model(
                        **encoded
                    ).logits
                )

                probabilities = (
                    self._torch
                    .softmax(
                        logits,
                        dim=-1,
                    )[0]
                )

                label_id = int(
                    self._torch
                    .argmax(
                        probabilities
                    )
                    .item()
                )

                score = float(
                    probabilities[
                        label_id
                    ].item()
                )

            raw_label = (
                self.model
                .config
                .id2label
                .get(
                    label_id,
                    str(label_id),
                )
            )

            return (
                str(raw_label),
                score,
            )

        prediction = (
            self.classifier(
                clause_text,
                ZERO_SHOT_LABELS,
                multi_label=False,
            )
        )

        return (
            str(
                prediction[
                    "labels"
                ][0]
            ),
            float(
                prediction[
                    "scores"
                ][0]
            ),
        )


    def classify(
        self,
        clauses,
        offsets,
    ):

        if (
            len(clauses)
            != len(offsets)
        ):
            raise ValueError(
                "clauses and offsets "
                "must have the same length."
            )

        results = []

        for (
            clause_text,
            (start, end),
        ) in zip(
            clauses,
            offsets,
        ):

            if not clause_text.strip():
                continue

            (
                raw_label,
                score,
            ) = self._predict(
                clause_text
            )

            results.append(
                ClauseSegment(
                    clause_id=(
                        str(
                            uuid.uuid4()
                        )[:8]
                    ),
                    text=(
                        clause_text
                    ),
                    clause_type=(
                        display_clause_label(
                            raw_label
                        )
                    ),
                    confidence=(
                        round(
                            score,
                            4,
                        )
                    ),
                    needs_review=(
                        score
                        < self.confidence_threshold
                    ),
                    start_char=(
                        start
                    ),
                    end_char=(
                        end
                    ),
                )
            )

        return results


def classifier_from_environment():

    model_path = (
        os.getenv(
            "CLAUSE_MODEL_PATH"
        )
        or None
    )

    threshold = float(
        os.getenv(
            "CLAUSE_CONFIDENCE_THRESHOLD",
            "0.50",
        )
    )

    return ClauseClassifier(
        model_name_or_path=(
            model_path
        ),
        confidence_threshold=(
            threshold
        ),
    )