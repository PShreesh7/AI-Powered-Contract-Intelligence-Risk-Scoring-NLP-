import spacy
import pytest

from app.ner.entity_extractor import EntityExtractor


def _build_test_nlp():
    """
    Create a small deterministic spaCy pipeline for testing.

    We do not use en_core_web_sm here because automated tests
    should not depend on a separately downloaded model.
    """
    nlp = spacy.blank("en")

    ruler = nlp.add_pipe("entity_ruler")

    ruler.add_patterns(
        [
            {
                "label": "ORG",
                "pattern": "Acme Corp",
            },
            {
                "label": "DATE",
                "pattern": "January 5, 2024",
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


def test_entity_extractor_maps_spacy_labels(monkeypatch):
    monkeypatch.setattr(
        spacy,
        "load",
        lambda _: _build_test_nlp(),
    )

    extractor = EntityExtractor("test-model")

    text = (
        "Acme Corp signed on January 5, 2024 "
        "in Delaware for $10,000."
    )

    entities = extractor.extract(text)

    found = {
        (entity.text, entity.label)
        for entity in entities
    }

    assert ("Acme Corp", "PARTY") in found
    assert ("January 5, 2024", "DATE") in found
    assert ("Delaware", "JURISDICTION") in found
    assert ("$10,000", "MONEY") in found


def test_entity_extractor_preserves_offsets(monkeypatch):
    monkeypatch.setattr(
        spacy,
        "load",
        lambda _: _build_test_nlp(),
    )

    extractor = EntityExtractor("test-model")

    text = "Acme Corp signed the agreement."

    entity = next(
        e
        for e in extractor.extract(text)
        if e.text == "Acme Corp"
    )

    assert (
        text[entity.start_char:entity.end_char]
        == "Acme Corp"
    )

    assert entity.confidence == 1.0


def test_entity_extractor_adds_regex_jurisdiction(
    monkeypatch,
):
    monkeypatch.setattr(
        spacy,
        "load",
        lambda _: spacy.blank("en"),
    )

    extractor = EntityExtractor("test-model")

    text = (
        "This Agreement shall be governed "
        "by Delaware."
    )

    entities = extractor.extract(text)

    jurisdiction = next(
        e
        for e in entities
        if e.label == "JURISDICTION"
    )

    assert jurisdiction.text == "Delaware"

    assert (
        text[
            jurisdiction.start_char:
            jurisdiction.end_char
        ]
        == "Delaware"
    )

    assert jurisdiction.confidence == 0.8


def test_entity_extractor_reports_missing_spacy_model(
    monkeypatch,
):
    def raise_missing_model(_):
        raise OSError("model not found")

    monkeypatch.setattr(
        spacy,
        "load",
        raise_missing_model,
    )

    with pytest.raises(
        RuntimeError,
        match="spaCy model 'missing-model' not found",
    ):
        EntityExtractor("missing-model")