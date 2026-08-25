import spacy
import pytest

from app.ner.entity_extractor import (
    EntityExtractor,
)


def build_test_nlp():

    nlp = spacy.blank(
        "en"
    )

    ruler = nlp.add_pipe(
        "entity_ruler"
    )

    ruler.add_patterns(
        [
            {
                "label": "ORG",
                "pattern": "Acme Corp",
            },
            {
                "label": "DATE",
                "pattern": (
                    "January 5, 2024"
                ),
            },
            {
                "label": "GPE",
                "pattern": "Delaware",
            },
            {
                "label": "MONEY",
                "pattern": "$10,000",
            },
        ]
    )

    return nlp


def test_label_mapping(
    monkeypatch,
):

    monkeypatch.setattr(
        spacy,
        "load",
        lambda _: build_test_nlp(),
    )

    extractor = EntityExtractor(
        "test-model"
    )

    text = (
        "Acme Corp signed on "
        "January 5, 2024 "
        "in Delaware "
        "for $10,000."
    )

    entities = extractor.extract(
        text
    )

    found = {
        (
            entity.text,
            entity.label,
        )
        for entity in entities
    }

    assert (
        "Acme Corp",
        "PARTY",
    ) in found

    assert (
        "Delaware",
        "JURISDICTION",
    ) in found

    assert (
        "$10,000",
        "MONEY",
    ) in found


def test_offsets(
    monkeypatch,
):

    monkeypatch.setattr(
        spacy,
        "load",
        lambda _: build_test_nlp(),
    )

    extractor = EntityExtractor(
        "test-model"
    )

    text = (
        "Acme Corp signed "
        "the agreement."
    )

    entity = next(
        entity
        for entity
        in extractor.extract(text)
        if entity.text
        == "Acme Corp"
    )

    assert (
        text[
            entity.start_char:
            entity.end_char
        ]
        == "Acme Corp"
    )


def test_regex_jurisdiction(
    monkeypatch,
):

    monkeypatch.setattr(
        spacy,
        "load",
        lambda _: spacy.blank(
            "en"
        ),
    )

    extractor = EntityExtractor(
        "test-model"
    )

    text = (
        "This Agreement shall "
        "be governed by Delaware."
    )

    entities = extractor.extract(
        text
    )

    entity = next(
        entity
        for entity in entities
        if entity.label
        == "JURISDICTION"
    )

    assert (
        entity.text
        == "Delaware"
    )


def test_deduplication(
    monkeypatch,
):

    nlp = spacy.blank(
        "en"
    )

    ruler = nlp.add_pipe(
        "entity_ruler"
    )

    ruler.add_patterns(
        [
            {
                "label": "GPE",
                "pattern": "Delaware",
            }
        ]
    )

    monkeypatch.setattr(
        spacy,
        "load",
        lambda _: nlp,
    )

    extractor = EntityExtractor(
        "test-model"
    )

    text = (
        "This Agreement is "
        "governed by Delaware."
    )

    entities = [
        entity
        for entity
        in extractor.extract(text)
        if (
            entity.label
            == "JURISDICTION"
            and entity.text
            == "Delaware"
        )
    ]

    assert len(entities) == 1


def test_blank_text(
    monkeypatch,
):

    monkeypatch.setattr(
        spacy,
        "load",
        lambda _: spacy.blank(
            "en"
        ),
    )

    extractor = EntityExtractor(
        "test-model"
    )

    assert (
        extractor.extract("   ")
        == []
    )


def test_missing_model(
    monkeypatch,
):

    def raise_error(_):
        raise OSError(
            "not found"
        )

    monkeypatch.setattr(
        spacy,
        "load",
        raise_error,
    )

    with pytest.raises(
        RuntimeError
    ):
        EntityExtractor(
            "missing-model"
        )