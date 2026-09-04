"""Semantic search service for legal contract clauses.

This module connects the embedding layer with the vector database layer.

Pipeline:

    contract clauses
        -> embeddings
        -> vector database

    user query
        -> query embedding
        -> vector similarity search
        -> ranked legal clauses
"""

from __future__ import annotations

from dataclasses import dataclass

from typing import (
    Any,
    Sequence,
)

from app.models.schemas import (
    ClauseSegment,
)

from app.search.embeddings import (
    EmbeddingService,
)

from app.search.vector_store import (
    PineconeVectorStore,
    VectorSearchMatch,
)


@dataclass(
    frozen=True
)
class SemanticSearchResult:
    """One ranked semantic-search result."""

    rank: int

    vector_id: str

    score: float

    document_id: str

    clause_id: str

    clause_type: str

    text: str

    filename: str | None

    confidence: float | None

    needs_review: bool | None

    start_char: int | None

    end_char: int | None

    metadata: dict[
        str,
        Any,
    ]


class SemanticSearchService:
    """Index and semantically search legal contract clauses."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: PineconeVectorStore,
    ) -> None:

        self.embedding_service = (
            embedding_service
        )

        self.vector_store = (
            vector_store
        )

        self._validate_dimensions()

    def _validate_dimensions(
        self,
    ) -> None:
        """Ensure embedding and vector-store dimensions agree."""

        embedding_dimension = (
            self.embedding_service
            .dimension
        )

        vector_dimension = (
            self.vector_store
            .dimension
        )

        if (
            embedding_dimension
            != vector_dimension
        ):
            raise ValueError(
                "Embedding dimension "
                "does not match vector "
                "store dimension. "
                f"Embedding service: "
                f"{embedding_dimension}, "
                f"vector store: "
                f"{vector_dimension}."
            )

    @staticmethod
    def _validate_query(
        query: str,
    ) -> str:
        """Validate and clean a semantic-search query."""

        if not isinstance(
            query,
            str,
        ):
            raise TypeError(
                "query must be a string."
            )

        cleaned = query.strip()

        if not cleaned:
            raise ValueError(
                "query must not be empty."
            )

        return cleaned

    def index_clauses(
        self,
        *,
        document_id: str,
        clauses: Sequence[
            ClauseSegment
        ],
        filename: str | None = None,
        batch_size: int = 100,
    ) -> int:
        """Generate and store embeddings for classified clauses."""

        if batch_size <= 0:
            raise ValueError(
                "batch_size must be "
                "greater than zero."
            )

        if not clauses:
            return 0

        embeddings = (
            self.embedding_service
            .embed_clauses(
                document_id=document_id,
                clauses=clauses,
                filename=filename,
            )
        )

        return (
            self.vector_store
            .upsert_embeddings(
                embeddings,
                batch_size=batch_size,
            )
        )

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        document_id: str | None = None,
        clause_type: str | None = None,
        min_score: float | None = None,
        metadata_filter: dict[
            str,
            Any,
        ] | None = None,
    ) -> list[
        SemanticSearchResult
    ]:
        """Search indexed contract clauses using natural language."""

        cleaned_query = (
            self._validate_query(
                query
            )
        )

        if top_k <= 0:
            raise ValueError(
                "top_k must be "
                "greater than zero."
            )

        query_vector = (
            self.embedding_service
            .embed_text(
                cleaned_query
            )
        )

        matches = (
            self.vector_store
            .query(
                query_vector,
                top_k=top_k,
                document_id=(
                    document_id
                ),
                clause_type=(
                    clause_type
                ),
                metadata_filter=(
                    metadata_filter
                ),
            )
        )

        results = []

        for match in matches:

            if (
                min_score is not None
                and match.score
                < min_score
            ):
                continue

            results.append(
                self._to_result(
                    match=match,
                    rank=(
                        len(results)
                        + 1
                    ),
                )
            )

        return results

    @staticmethod
    def _to_result(
        *,
        match: VectorSearchMatch,
        rank: int,
    ) -> SemanticSearchResult:
        """Convert vector-store output into API-friendly search data."""

        metadata = dict(
            match.metadata
        )

        confidence = (
            metadata.get(
                "confidence"
            )
        )

        if confidence is not None:
            confidence = float(
                confidence
            )

        start_char = (
            metadata.get(
                "start_char"
            )
        )

        if start_char is not None:
            start_char = int(
                start_char
            )

        end_char = (
            metadata.get(
                "end_char"
            )
        )

        if end_char is not None:
            end_char = int(
                end_char
            )

        needs_review = (
            metadata.get(
                "needs_review"
            )
        )

        if needs_review is not None:
            needs_review = bool(
                needs_review
            )

        filename = metadata.get(
            "filename"
        )

        if filename is not None:
            filename = str(
                filename
            )

        return SemanticSearchResult(
            rank=rank,
            vector_id=(
                match.vector_id
            ),
            score=float(
                match.score
            ),
            document_id=str(
                metadata.get(
                    "document_id",
                    "",
                )
            ),
            clause_id=str(
                metadata.get(
                    "clause_id",
                    "",
                )
            ),
            clause_type=str(
                metadata.get(
                    "clause_type",
                    "",
                )
            ),
            text=str(
                metadata.get(
                    "text",
                    "",
                )
            ),
            filename=filename,
            confidence=confidence,
            needs_review=(
                needs_review
            ),
            start_char=(
                start_char
            ),
            end_char=end_char,
            metadata=metadata,
        )

    def delete_document(
        self,
        document_id: str,
    ) -> None:
        """Delete all indexed vectors for one contract."""

        self.vector_store.delete_document(
            document_id
        )

    def describe_stats(
        self,
    ) -> Any:
        """Return vector database statistics."""

        return (
            self.vector_store
            .describe_stats()
        )