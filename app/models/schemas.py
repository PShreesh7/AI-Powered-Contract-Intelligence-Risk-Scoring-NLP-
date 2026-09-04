from __future__ import annotations

from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from pydantic import (
    BaseModel,
    Field,
)


class ExtractedEntity(
    BaseModel
):
    label: str

    text: str

    start_char: int

    end_char: int

    confidence: Optional[
        float
    ] = None


class ClauseSegment(
    BaseModel
):
    clause_id: str

    text: str

    clause_type: str

    confidence: float

    needs_review: bool = False

    start_char: int

    end_char: int


class RiskFlag(
    BaseModel
):
    clause_id: str

    risk_level: str

    reason: str

    suggestion: Optional[
        str
    ] = None


class DocumentAnalysis(
    BaseModel
):
    document_id: str

    filename: str

    raw_text_length: int

    entities: List[
        ExtractedEntity
    ] = Field(
        default_factory=list
    )

    clauses: List[
        ClauseSegment
    ] = Field(
        default_factory=list
    )

    risk_flags: List[
        RiskFlag
    ] = Field(
        default_factory=list
    )


class AnalyzeResponse(
    BaseModel
):
    status: str

    analysis: Optional[
        DocumentAnalysis
    ] = None

    error: Optional[
        str
    ] = None


class AnalyzeAndIndexResponse(
    BaseModel
):
    """Response after analyzing and indexing a contract."""

    status: str

    analysis: DocumentAnalysis

    indexed_count: int


class SemanticSearchRequest(
    BaseModel
):
    """Natural-language semantic search request."""

    query: str = Field(
        min_length=1
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
    )

    document_id: Optional[
        str
    ] = None

    clause_type: Optional[
        str
    ] = None

    min_score: Optional[
        float
    ] = Field(
        default=None,
        ge=-1.0,
        le=1.0,
    )

    metadata_filter: Optional[
        Dict[
            str,
            Any,
        ]
    ] = None


class SemanticSearchHit(
    BaseModel
):
    """One ranked semantic-search result."""

    rank: int

    vector_id: str

    score: float

    document_id: str

    clause_id: str

    clause_type: str

    text: str

    filename: Optional[
        str
    ] = None

    confidence: Optional[
        float
    ] = None

    needs_review: Optional[
        bool
    ] = None

    start_char: Optional[
        int
    ] = None

    end_char: Optional[
        int
    ] = None

    metadata: Dict[
        str,
        Any,
    ] = Field(
        default_factory=dict
    )


class SemanticSearchResponse(
    BaseModel
):
    status: str

    query: str

    count: int

    results: List[
        SemanticSearchHit
    ] = Field(
        default_factory=list
    )


class SearchStatsResponse(
    BaseModel
):
    status: str

    stats: Dict[
        str,
        Any,
    ] = Field(
        default_factory=dict
    )