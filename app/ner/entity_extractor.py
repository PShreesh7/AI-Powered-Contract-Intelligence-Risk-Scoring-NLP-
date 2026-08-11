"""
Day 2 module: Named Entity Recognition.
Uses spaCy as the base extractor (fast, good at DATE/ORG/GPE/MONEY out of the box)
and adds regex-based extractors for legal-specific patterns spaCy misses,
like "Party of the First Part" style phrasing and jurisdiction clauses.

To upgrade later: swap `nlp` for a legal-domain transformer, e.g.
`nlpaueb/legal-bert-base-uncased` fine-tuned for token classification,
loaded via transformers' AutoModelForTokenClassification + pipeline("ner").
"""
from __future__ import annotations
import re
from typing import List
import spacy

from app.models.schemas import ExtractedEntity

# Map spaCy's default labels to our domain labels
LABEL_MAP = {
    "DATE": "DATE",
    "ORG": "PARTY",
    "PERSON": "PARTY",
    "GPE": "JURISDICTION",
    "LOC": "JURISDICTION",
    "MONEY": "MONEY",
}

JURISDICTION_PATTERN = re.compile(
    r"(?:governed by|governing law|laws of|jurisdiction of)\s+(?:the\s+)?([A-Z][A-Za-z\s]{2,40})",
    re.IGNORECASE,
)


class EntityExtractor:
    def __init__(self, model_name: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model_name)
        except OSError as e:
            raise RuntimeError(
                f"spaCy model '{model_name}' not found. Run: "
                f"python -m spacy download {model_name}"
            ) from e

    def extract(self, text: str) -> List[ExtractedEntity]:
        entities: List[ExtractedEntity] = []
        doc = self.nlp(text)

        for ent in doc.ents:
            mapped_label = LABEL_MAP.get(ent.label_)
            if mapped_label:
                entities.append(
                    ExtractedEntity(
                        label=mapped_label,
                        text=ent.text,
                        start_char=ent.start_char,
                        end_char=ent.end_char,
                        confidence=1.0,  # spaCy doesn't expose per-entity confidence by default
                    )
                )

        # Supplement with regex-based jurisdiction detection
        for match in JURISDICTION_PATTERN.finditer(text):
            entities.append(
                ExtractedEntity(
                    label="JURISDICTION",
                    text=match.group(1).strip(),
                    start_char=match.start(1),
                    end_char=match.end(1),
                    confidence=0.8,
                )
            )

        return entities


if __name__ == "__main__":
    sample = (
        "This Agreement is entered into on January 5, 2024 between Acme Corp "
        "and Beta LLC. This Agreement shall be governed by the laws of Delaware."
    )
    extractor = EntityExtractor()
    for e in extractor.extract(sample):
        print(e)
