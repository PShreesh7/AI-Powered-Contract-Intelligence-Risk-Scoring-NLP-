from __future__ import annotations

import argparse
import json
import random

from pathlib import Path

import torch

from torch.utils.data import (
    Dataset,
)

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

from app.preprocessing.clause_dataset import (
    load_jsonl,
)

from app.training.metrics import (
    trainer_metrics,
)


DEFAULT_MODEL = (
    "nlpaueb/"
    "legal-bert-base-uncased"
)


class ClauseClassificationDataset(
    Dataset
):

    def __init__(
        self,
        records,
        tokenizer,
        max_length=256,
    ):

        self.records = records
        self.tokenizer = tokenizer
        self.max_length = (
            max_length
        )


    def __len__(
        self,
    ):

        return len(
            self.records
        )


    def __getitem__(
        self,
        index,
    ):

        record = (
            self.records[
                index
            ]
        )

        encoded = (
            self.tokenizer(
                record["text"],
                truncation=True,
                padding="max_length",
                max_length=(
                    self.max_length
                ),
                return_tensors="pt",
            )
        )

        item = {
            key: value.squeeze(
                0
            )
            for key, value
            in encoded.items()
        }

        item["labels"] = (
            torch.tensor(
                int(
                    record[
                        "label_id"
                    ]
                ),
                dtype=torch.long,
            )
        )

        return item


def load_label_mapping(
    path,
):

    with Path(path).open(
        "r",
        encoding="utf-8",
    ) as file:

        mapping = json.load(
            file
        )

    label2id = {
        str(key): int(
            value
        )
        for key, value
        in mapping[
            "label2id"
        ].items()
    }

    id2label = {
        int(key): str(
            value
        )
        for key, value
        in mapping[
            "id2label"
        ].items()
    }

    return (
        label2id,
        id2label,
    )


def train_clause_classifier(
    data_dir,
    output_dir,
    *,
    model_name=DEFAULT_MODEL,
    max_length=256,
    learning_rate=2e-5,
    train_batch_size=8,
    eval_batch_size=8,
    num_epochs=3,
    seed=42,
):

    data_dir = Path(
        data_dir
    )

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    train_records = (
        load_jsonl(
            data_dir
            / "train.jsonl"
        )
    )

    validation_records = (
        load_jsonl(
            data_dir
            / "validation.jsonl"
        )
    )

    if not train_records:
        raise ValueError(
            "Training split is empty."
        )

    if not validation_records:
        raise ValueError(
            "Validation split is empty."
        )

    (
        label2id,
        id2label,
    ) = load_label_mapping(
        data_dir
        / "labels.json"
    )

    random.seed(
        seed
    )

    torch.manual_seed(
        seed
    )

    tokenizer = (
        AutoTokenizer
        .from_pretrained(
            model_name
        )
    )

    model = (
        AutoModelForSequenceClassification
        .from_pretrained(
            model_name,
            num_labels=(
                len(label2id)
            ),
            label2id=(
                label2id
            ),
            id2label=(
                id2label
            ),
        )
    )

    train_dataset = (
        ClauseClassificationDataset(
            train_records,
            tokenizer,
            max_length,
        )
    )

    validation_dataset = (
        ClauseClassificationDataset(
            validation_records,
            tokenizer,
            max_length,
        )
    )

    training_args = (
        TrainingArguments(
            output_dir=str(
                output_dir
            ),
            learning_rate=(
                learning_rate
            ),
            per_device_train_batch_size=(
                train_batch_size
            ),
            per_device_eval_batch_size=(
                eval_batch_size
            ),
            num_train_epochs=(
                num_epochs
            ),
            weight_decay=0.01,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model=(
                "macro_f1"
            ),
            greater_is_better=True,
            save_total_limit=1,
            logging_steps=100,
            seed=seed,
            report_to="none",
            dataloader_pin_memory=False,
        )
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=(
            train_dataset
        ),
        eval_dataset=(
            validation_dataset
        ),
        tokenizer=tokenizer,
        compute_metrics=(
            trainer_metrics
        ),
    )

    train_result = (
        trainer.train()
    )

    validation_metrics = (
        trainer.evaluate()
    )

    trainer.save_model(
        str(output_dir)
    )

    tokenizer.save_pretrained(
        str(output_dir)
    )

    with (
        output_dir
        / "labels.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            {
                "label2id": (
                    label2id
                ),
                "id2label": {
                    str(key): value
                    for key, value
                    in id2label.items()
                },
            },
            file,
            indent=2,
        )

    summary = {
        "model_name": (
            model_name
        ),
        "train_examples": (
            len(
                train_records
            )
        ),
        "validation_examples": (
            len(
                validation_records
            )
        ),
        "num_labels": (
            len(label2id)
        ),
        "train_metrics": (
            train_result.metrics
        ),
        "validation_metrics": (
            validation_metrics
        ),
    }

    with (
        output_dir
        / "training_summary.json"
    ).open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=2,
            default=float,
        )

    return summary


def main():

    parser = (
        argparse.ArgumentParser()
    )

    parser.add_argument(
        "--data-dir",
        required=True,
    )

    parser.add_argument(
        "--output-dir",
        required=True,
    )

    parser.add_argument(
        "--model-name",
        default=DEFAULT_MODEL,
    )

    parser.add_argument(
        "--max-length",
        type=int,
        default=256,
    )

    parser.add_argument(
        "--learning-rate",
        type=float,
        default=2e-5,
    )

    parser.add_argument(
        "--train-batch-size",
        type=int,
        default=8,
    )

    parser.add_argument(
        "--eval-batch-size",
        type=int,
        default=8,
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )

    args = (
        parser.parse_args()
    )

    summary = (
        train_clause_classifier(
            args.data_dir,
            args.output_dir,
            model_name=(
                args.model_name
            ),
            max_length=(
                args.max_length
            ),
            learning_rate=(
                args.learning_rate
            ),
            train_batch_size=(
                args.train_batch_size
            ),
            eval_batch_size=(
                args.eval_batch_size
            ),
            num_epochs=(
                args.epochs
            ),
            seed=args.seed,
        )
    )

    print(
        json.dumps(
            summary,
            indent=2,
            default=float,
        )
    )


if __name__ == "__main__":
    main()