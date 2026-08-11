"""
Shared data models used across the ingestion -> NER -> clause -> risk pipeline.
Keeping these in one place means every module speaks the same contract.
"""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class ExtractedEntity(BaseModel):
    label: str            # e.g. "DATE", "PARTY", "JURISDICTION", "MONEY"
    text: str              # raw matched text
    start_char: int
    end_char: int
    confidence: Optional[float] = None


class ClauseSegment(BaseModel):
    clause_id: str
    text: str
    clause_type: str       # e.g. "termination", "confidentiality", "indemnification"
    confidence: float
    start_char: int
    end_char: int


class RiskFlag(BaseModel):
    clause_id: str
    risk_level: str         # "low" | "medium" | "high"
    reason: str              # short explanation of why it was flagged
    suggestion: Optional[str] = None


class DocumentAnalysis(BaseModel):
    document_id: str
    filename: str
    raw_text_length: int
    entities: List[ExtractedEntity] = Field(default_factory=list)
    clauses: List[ClauseSegment] = Field(default_factory=list)
    risk_flags: List[RiskFlag] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    status: str
    analysis: Optional[DocumentAnalysis] = None
    error: Optional[str] = None
