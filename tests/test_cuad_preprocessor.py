import json

from app.preprocessing.cuad_preprocessor import (
    flatten_cuad,
    load_cuad,
    preprocess_cuad,
)


def test_flatten_cuad():
    context = (
        "This Agreement shall be governed "
        "by the laws of Delaware."
    )

    answer_start = context.index("Delaware")

    dataset = {
        "data": [
            {
                "title": "sample_contract",
                "paragraphs": [
                    {
                        "context": context,
                        "qas": [
                            {
                                "id": "q1",
                                "question": (
                                    "What is the "
                                    "governing law?"
                                ),
                                "answers": [
                                    {
                                        "text": "Delaware",
                                        "answer_start": (
                                            answer_start
                                        ),
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ]
    }

    records = flatten_cuad(dataset)

    assert len(records) == 1

    record = records[0]

    assert record["id"] == "q1"

    assert (
        record["title"]
        == "sample_contract"
    )

    assert record["answers"]["text"] == [
        "Delaware"
    ]

    assert (
        record["answers"]["answer_start"]
        == [answer_start]
    )

    assert record["is_impossible"] is False


def test_load_cuad(tmp_path):
    input_file = tmp_path / "cuad.json"

    dataset = {
        "data": []
    }

    input_file.write_text(
        json.dumps(dataset),
        encoding="utf-8",
    )

    loaded = load_cuad(input_file)

    assert "data" in loaded
    assert loaded["data"] == []


def test_preprocess_cuad_writes_jsonl(
    tmp_path,
):
    input_file = (
        tmp_path / "cuad.json"
    )

    output_file = (
        tmp_path / "processed.jsonl"
    )

    dataset = {
        "data": [
            {
                "title": "sample",
                "paragraphs": [
                    {
                        "context": (
                            "Sample contract text."
                        ),
                        "qas": [
                            {
                                "id": "1",
                                "question": (
                                    "Sample question?"
                                ),
                                "answers": [],
                                "is_impossible": True,
                            }
                        ],
                    }
                ],
            }
        ]
    }

    input_file.write_text(
        json.dumps(dataset),
        encoding="utf-8",
    )

    count = preprocess_cuad(
        input_file,
        output_file,
    )

    assert count == 1
    assert output_file.exists()

    content = output_file.read_text(
        encoding="utf-8",
    ).strip()

    record = json.loads(content)

    assert record["id"] == "1"

    assert (
        record["is_impossible"]
        is True
    )