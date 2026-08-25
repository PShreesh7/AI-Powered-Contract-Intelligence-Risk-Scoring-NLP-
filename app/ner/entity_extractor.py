"""Legal entity extraction using spaCy and legal regex rules."""

from __future__ import annotations

import re
from typing import Iterable, List

import spacy

from app.models.schemas import (
    ExtractedEntity,
)


LABEL_MAP = {
    "DATE": "DATE",
    "ORG": "PARTY",
    "PERSON": "PARTY",
    "GPE": "JURISDICTION",
    "LOC": "JURISDICTION",
    "MONEY": "MONEY",
}


JURISDICTION_PATTERN = re.compile(
    r"(?:"
    r"governed\s+by"
    r"(?:\s+the\s+laws\s+of)?"
    r"|governing\s+law(?:\s+of)?"
    r"|laws\s+of"
    r"|jurisdiction\s+of"
    r")"
    r"\s+"
    r"(?:the\s+)?"
    r"(?P<jurisdiction>"
    r"[A-Z][A-Za-z .'-]{1,50}?"
    r")"
    r"(?=\s*(?:[.;,\n]|$))",
    re.IGNORECASE,
)


def _entity_key(
    entity: ExtractedEntity,
):
    return (
        entity.label,
        entity.start_char,
        entity.end_char,
    )


def deduplicate_entities(
    entities: Iterable[
        ExtractedEntity
    ],
) -> List[ExtractedEntity]:

    best = {}

    for entity in entities:

        key = _entity_key(
            entity
        )

        current = best.get(
            key
        )

        current_conf = (
            current.confidence
            if (
                current
                and current.confidence
                is not None
            )
            else -1.0
        )

        new_conf = (
            entity.confidence
            if entity.confidence
            is not None
            else -1.0
        )

        if (
            current is None
            or new_conf
            > current_conf
        ):
            best[key] = entity

    return sorted(
        best.values(),
        key=lambda item: (
            item.start_char,
            item.end_char,
            item.label,
        ),
    )


class EntityExtractor:

    def __init__(
        self,
        model_name="en_core_web_sm",
    ):

        try:
            self.nlp = spacy.load(
                model_name
            )

        except OSError as exc:

            raise RuntimeError(
                f"spaCy model "
                f"'{model_name}' not found. "
                f"Run: python -m spacy "
                f"download {model_name}"
            ) from exc


    def extract(
        self,
        text: str,
    ) -> List[ExtractedEntity]:

        if not text.strip():
            return []

        entities = []

        doc = self.nlp(
            text
        )

        for ent in doc.ents:

            mapped_label = (
                LABEL_MAP.get(
                    ent.label_
                )
            )

            if not mapped_label:
                continue

            entities.append(
                ExtractedEntity(
                    label=mapped_label,
                    text=ent.text,
                    start_char=(
                        ent.start_char
                    ),
                    end_char=(
                        ent.end_char
                    ),
                    confidence=1.0,
                )
            )

        for match in (
            JURISDICTION_PATTERN
            .finditer(text)
        ):

            start, end = (
                match.span(
                    "jurisdiction"
                )
            )

            jurisdiction = (
                text[start:end]
                .rstrip()
            )

            end = (
                start
                + len(jurisdiction)
            )

            if not jurisdiction:
                continue

            entities.append(
                ExtractedEntity(
                    label=(
                        "JURISDICTION"
                    ),
                    text=jurisdiction,
                    start_char=start,
                    end_char=end,
                    confidence=0.8,
                )
            )

        return deduplicate_entities(
            entities
        )