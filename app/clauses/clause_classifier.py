"""
Day 3 module: clause type classification.
Starts with zero-shot classification (facebook/bart-large-mnli) against a fixed
label set of common contract clause types -- no training data needed to get
a working demo. Swap `zero_shot` for a fine-tuned classifier once your team
has labeled examples (see docs/ARCHITECTURE.md for the upgrade path).
"""
from __future__ import annotations
import uuid
from typing import List
from transformers import pipeline

from app.models.schemas import ClauseSegment

CLAUSE_LABELS = [
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


class ClauseClassifier:
    def __init__(self, model_name: str = "facebook/bart-large-mnli"):
        self.classifier = pipeline("zero-shot-classification", model=model_name)

    def classify(self, clauses: List[str], offsets: List[tuple]) -> List[ClauseSegment]:
        """
        clauses: list of clause text chunks
        offsets: list of (start_char, end_char) matching each clause, same order
        """
        results: List[ClauseSegment] = []

        for clause_text, (start, end) in zip(clauses, offsets):
            prediction = self.classifier(clause_text, CLAUSE_LABELS, multi_label=False)
            top_label = prediction["labels"][0]
            top_score = float(prediction["scores"][0])

            results.append(
                ClauseSegment(
                    clause_id=str(uuid.uuid4())[:8],
                    text=clause_text,
                    clause_type=top_label,
                    confidence=round(top_score, 3),
                    start_char=start,
                    end_char=end,
                )
            )

        return results


if __name__ == "__main__":
    sample_clauses = [
        "Either party may terminate this Agreement upon 30 days written notice.",
        "Each party agrees to keep confidential all proprietary information disclosed by the other party.",
    ]
    offsets = [(0, len(sample_clauses[0])), (0, len(sample_clauses[1]))]
    clf = ClauseClassifier()
    for c in clf.classify(sample_clauses, offsets):
        print(c.clause_type, c.confidence)
