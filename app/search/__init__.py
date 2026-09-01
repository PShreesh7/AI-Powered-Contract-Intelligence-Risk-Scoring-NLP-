"""Semantic search infrastructure."""

from app.search.embeddings import (
    DEFAULT_EMBEDDING_MODEL,
    ClauseEmbedding,
    EmbeddingService,
)

from app.search.vector_store import (
    DEFAULT_DIMENSION,
    DEFAULT_INDEX_NAME,
    DEFAULT_NAMESPACE,
    PineconeVectorStore,
    VectorSearchMatch,
    vector_store_from_environment,
)


__all__ = [
    "DEFAULT_EMBEDDING_MODEL",
    "ClauseEmbedding",
    "EmbeddingService",
    "DEFAULT_DIMENSION",
    "DEFAULT_INDEX_NAME",
    "DEFAULT_NAMESPACE",
    "PineconeVectorStore",
    "VectorSearchMatch",
    "vector_store_from_environment",
]