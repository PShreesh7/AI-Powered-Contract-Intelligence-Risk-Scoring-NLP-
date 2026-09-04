from __future__ import annotations

import os
from dotenv import load_dotenv
load_dotenv()
from dataclasses import dataclass

from typing import (
    Any,
    Mapping,
    Sequence,
)

from app.search.embeddings import (
    ClauseEmbedding,
)


DEFAULT_INDEX_NAME = (
    "contract-intelligence"
)

DEFAULT_NAMESPACE = (
    "contracts"
)

DEFAULT_CLOUD = "aws"

DEFAULT_REGION = (
    "us-east-1"
)

DEFAULT_DIMENSION = 384

DEFAULT_METRIC = "cosine"


@dataclass(
    frozen=True
)
class VectorSearchMatch:
    """Normalized representation of one Pinecone search result."""

    vector_id: str

    score: float

    metadata: dict[
        str,
        Any,
    ]


class PineconeVectorStore:
    """Store and retrieve contract clause embeddings in Pinecone."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        index_name: str = DEFAULT_INDEX_NAME,
        namespace: str = DEFAULT_NAMESPACE,
        dimension: int = DEFAULT_DIMENSION,
        metric: str = DEFAULT_METRIC,
        cloud: str = DEFAULT_CLOUD,
        region: str = DEFAULT_REGION,
        client: Any | None = None,
        index: Any | None = None,
        auto_create: bool = False,
    ) -> None:

        index_name = index_name.strip()
        namespace = namespace.strip()
        cloud = cloud.strip()
        region = region.strip()

        if not index_name:
            raise ValueError(
                "index_name must not be empty."
            )

        if not namespace:
            raise ValueError(
                "namespace must not be empty."
            )

        if dimension <= 0:
            raise ValueError(
                "dimension must be greater than zero."
            )

        if metric not in {
            "cosine",
            "euclidean",
            "dotproduct",
        }:
            raise ValueError(
                "metric must be cosine, "
                "euclidean, or dotproduct."
            )

        if not cloud:
            raise ValueError(
                "cloud must not be empty."
            )

        if not region:
            raise ValueError(
                "region must not be empty."
            )

        self.index_name = index_name

        self.namespace = namespace

        self.dimension = dimension

        self.metric = metric

        self.cloud = cloud

        self.region = region

        self._client = (
            client
            if client is not None
            else self._build_client(
                api_key
            )
        )

        self._index = index

        if auto_create:
            self.ensure_index()

        if self._index is None:
            self._index = (
                self._get_index()
            )

    @staticmethod
    def _build_client(
        api_key: str | None,
    ) -> Any:
        """Create the Pinecone control-plane client."""

        api_key = (
            api_key
            or os.getenv(
                "PINECONE_API_KEY"
            )
        )

        if not api_key:
            raise ValueError(
                "PINECONE_API_KEY is required."
            )

        try:
            from pinecone import Pinecone

        except ImportError as exc:
            raise RuntimeError(
                "pinecone package is required. "
                "Install dependencies with: "
                "pip install -r requirements.txt"
            ) from exc

        return Pinecone(
            api_key=api_key
        )

    def _get_index(
        self,
    ) -> Any:
        """Return the Pinecone data-plane index client."""

        return self._client.index(
            self.index_name
        )

    def ensure_index(
        self,
    ) -> None:
        """Create the serverless index when it does not exist."""

        existing_names = {
            getattr(
                item,
                "name",
                None,
            )
            for item
            in self._client.indexes.list()
        }

        if (
            self.index_name
            not in existing_names
        ):

            try:
                from pinecone import (
                    ServerlessSpec,
                )

            except ImportError as exc:
                raise RuntimeError(
                    "pinecone package is required."
                ) from exc

            self._client.indexes.create(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=ServerlessSpec(
                    cloud=self.cloud,
                    region=self.region,
                ),
            )

        if self._index is None:
            self._index = (
                self._get_index()
            )

    def _validate_vector(
        self,
        vector: Sequence[float],
    ) -> list[float]:
        """Validate and normalize a dense vector."""

        values = [
            float(value)
            for value
            in vector
        ]

        if (
            len(values)
            != self.dimension
        ):
            raise ValueError(
                "Vector dimension mismatch. "
                f"Expected {self.dimension}, "
                f"received {len(values)}."
            )

        return values

    def upsert_embeddings(
        self,
        records: Sequence[
            ClauseEmbedding
        ],
        *,
        batch_size: int = 100,
    ) -> int:
        """Insert or update clause embeddings."""

        if batch_size <= 0:
            raise ValueError(
                "batch_size must be "
                "greater than zero."
            )

        if not records:
            return 0

        vectors = []

        for record in records:

            values = (
                self._validate_vector(
                    record.values
                )
            )

            vectors.append(
                {
                    "id": (
                        record.vector_id
                    ),
                    "values": values,
                    "metadata": dict(
                        record.metadata
                    ),
                }
            )

        response = (
            self._index.upsert(
                vectors=vectors,
                namespace=(
                    self.namespace
                ),
                batch_size=batch_size,
                show_progress=False,
            )
        )

        count = self._get_value(
            response,
            "upserted_count",
            len(records),
        )

        return int(
            count
        )

    def query(
        self,
        vector: Sequence[float],
        *,
        top_k: int = 5,
        document_id: str | None = None,
        clause_type: str | None = None,
        metadata_filter: dict[
            str,
            Any,
        ] | None = None,
    ) -> list[
        VectorSearchMatch
    ]:
        """Query Pinecone using an already-generated embedding."""

        if top_k <= 0:
            raise ValueError(
                "top_k must be "
                "greater than zero."
            )

        values = (
            self._validate_vector(
                vector
            )
        )

        filter_expression = (
            self._build_filter(
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

        query_kwargs = {
            "vector": values,
            "top_k": top_k,
            "namespace": (
                self.namespace
            ),
            "include_metadata": True,
            "include_values": False,
        }

        if filter_expression:
            query_kwargs[
                "filter"
            ] = filter_expression

        response = (
            self._index.query(
                **query_kwargs
            )
        )

        raw_matches = (
            self._get_value(
                response,
                "matches",
                [],
            )
            or []
        )

        matches = []

        for match in raw_matches:

            vector_id = str(
                self._get_value(
                    match,
                    "id",
                    "",
                )
            )

            score = float(
                self._get_value(
                    match,
                    "score",
                    0.0,
                )
            )

            metadata = (
                self._get_value(
                    match,
                    "metadata",
                    {},
                )
                or {}
            )

            matches.append(
                VectorSearchMatch(
                    vector_id=(
                        vector_id
                    ),
                    score=score,
                    metadata=dict(
                        metadata
                    ),
                )
            )

        return matches

    def delete_document(
        self,
        document_id: str,
    ) -> None:
        """Delete every clause vector belonging to a document."""

        document_id = (
            document_id.strip()
        )

        if not document_id:
            raise ValueError(
                "document_id must "
                "not be empty."
            )

        self._index.delete(
            filter={
                "document_id": {
                    "$eq": document_id
                }
            },
            namespace=(
                self.namespace
            ),
        )

    def delete_vectors(
        self,
        vector_ids: Sequence[str],
    ) -> None:
        """Delete specific vectors by identifier."""

        ids = [
            vector_id.strip()
            for vector_id
            in vector_ids
            if vector_id.strip()
        ]

        if not ids:
            return

        self._index.delete(
            ids=ids,
            namespace=(
                self.namespace
            ),
        )

    def describe_stats(
        self,
    ) -> Any:
        """Return Pinecone index statistics."""

        return (
            self._index
            .describe_index_stats()
        )

    @staticmethod
    def _get_value(
        obj: Any,
        key: str,
        default: Any = None,
    ) -> Any:
        """Read values from SDK objects or dictionaries."""

        if isinstance(
            obj,
            Mapping,
        ):
            return obj.get(
                key,
                default,
            )

        return getattr(
            obj,
            key,
            default,
        )

    @staticmethod
    def _build_filter(
        *,
        document_id: str | None,
        clause_type: str | None,
        metadata_filter: dict[
            str,
            Any,
        ] | None,
    ) -> dict[
        str,
        Any,
    ] | None:
        """Combine optional metadata filters."""

        conditions = []

        if metadata_filter:
            conditions.append(
                metadata_filter
            )

        if document_id:

            document_id = (
                document_id.strip()
            )

            if document_id:
                conditions.append(
                    {
                        "document_id": {
                            "$eq": (
                                document_id
                            )
                        }
                    }
                )

        if clause_type:

            clause_type = (
                clause_type.strip()
            )

            if clause_type:
                conditions.append(
                    {
                        "clause_type": {
                            "$eq": (
                                clause_type
                            )
                        }
                    }
                )

        if not conditions:
            return None

        if len(
            conditions
        ) == 1:
            return conditions[0]

        return {
            "$and": conditions
        }


def vector_store_from_environment(
    *,
    dimension: int = (
        DEFAULT_DIMENSION
    ),
    auto_create: bool = True,
) -> PineconeVectorStore:
    """Build PineconeVectorStore using environment variables."""

    api_key = os.getenv(
        "PINECONE_API_KEY"
    )

    if not api_key:
        raise ValueError(
            "PINECONE_API_KEY is required."
        )

    return PineconeVectorStore(
        api_key=api_key,
        index_name=os.getenv(
            "PINECONE_INDEX_NAME",
            DEFAULT_INDEX_NAME,
        ),
        namespace=os.getenv(
            "PINECONE_NAMESPACE",
            DEFAULT_NAMESPACE,
        ),
        dimension=dimension,
        metric=os.getenv(
            "PINECONE_METRIC",
            DEFAULT_METRIC,
        ),
        cloud=os.getenv(
            "PINECONE_CLOUD",
            DEFAULT_CLOUD,
        ),
        region=os.getenv(
            "PINECONE_REGION",
            DEFAULT_REGION,
        ),
        auto_create=auto_create,
    )