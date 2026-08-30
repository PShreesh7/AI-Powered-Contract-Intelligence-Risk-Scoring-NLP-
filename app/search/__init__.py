"""Semantic search utilities for contract embeddings and vector retrieval."""

from app.search.embeddings import (
    DEFAULT_EMBEDDING_MODEL,
    ClauseEmbedding,
    EmbeddingService,
)

__all__ = [
    "DEFAULT_EMBEDDING_MODEL",
    "ClauseEmbedding",
    "EmbeddingService",
]