"""Generate dense embeddings for contract clauses.

Day 11 adds only the embedding layer. The vectors produced here are
independent of a particular vector database so they can later be stored
in Pinecone, Milvus, or another vector backend.
"""

from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)

from typing import (
    Any,
    Iterable,
    Sequence,
)

import numpy as np

from app.models.schemas import (
    ClauseSegment,
)


DEFAULT_EMBEDDING_MODEL = (
    "sentence-transformers/"
    "all-MiniLM-L6-v2"
)


@dataclass(
    frozen=True
)
class ClauseEmbedding:
    """One contract clause and its dense embedding."""

    vector_id: str

    document_id: str

    clause_id: str

    text: str

    clause_type: str

    values: list[float]

    metadata: dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )


class EmbeddingService:
    """Generate semantic embeddings for legal contract text."""

    def __init__(
        self,
        model_name: str = (
            DEFAULT_EMBEDDING_MODEL
        ),
        *,
        batch_size: int = 32,
        normalize_embeddings: bool = True,
        model: Any | None = None,
    ) -> None:

        if batch_size <= 0:
            raise ValueError(
                "batch_size must be "
                "greater than zero."
            )

        self.model_name = (
            model_name
        )

        self.batch_size = (
            batch_size
        )

        self.normalize_embeddings = (
            normalize_embeddings
        )

        self._model = (
            model
            or self._load_model(
                model_name
            )
        )


    @staticmethod
    def _load_model(
        model_name: str,
    ) -> Any:

        try:
            from sentence_transformers import (
                SentenceTransformer,
            )

        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers is "
                "required for semantic "
                "embeddings. Install "
                "dependencies with: "
                "pip install -r "
                "requirements.txt"
            ) from exc

        return SentenceTransformer(
            model_name
        )


    @property
    def dimension(
        self,
    ) -> int:
        """Return embedding vector dimension."""

        get_dimension = getattr(
            self._model,
            (
                "get_sentence_"
                "embedding_dimension"
            ),
            None,
        )

        if callable(
            get_dimension
        ):

            dimension = (
                get_dimension()
            )

            if dimension is not None:
                return int(
                    dimension
                )

        probe = self.embed_text(
            "embedding dimension probe"
        )

        return len(
            probe
        )


    @staticmethod
    def _validate_texts(
        texts: Sequence[str],
    ) -> list[str]:

        validated = []

        for index, text in enumerate(
            texts
        ):

            if not isinstance(
                text,
                str,
            ):
                raise TypeError(
                    f"Text at index "
                    f"{index} must "
                    f"be a string."
                )

            cleaned = text.strip()

            if not cleaned:
                raise ValueError(
                    f"Text at index "
                    f"{index} is empty."
                )

            validated.append(
                cleaned
            )

        return validated


    def embed_texts(
        self,
        texts: Iterable[str],
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts."""

        validated = (
            self._validate_texts(
                list(texts)
            )
        )

        if not validated:
            return []

        vectors = (
            self._model.encode(
                validated,
                batch_size=(
                    self.batch_size
                ),
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=(
                    self
                    .normalize_embeddings
                ),
            )
        )

        array = np.asarray(
            vectors,
            dtype=np.float32,
        )

        if array.ndim == 1:
            array = array.reshape(
                1,
                -1,
            )

        if (
            array.ndim != 2
            or array.shape[0]
            != len(validated)
        ):
            raise RuntimeError(
                "Embedding model returned "
                "an unexpected output "
                f"shape: {array.shape}."
            )

        return array.tolist()


    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        """Generate embedding for one text."""

        return (
            self.embed_texts(
                [text]
            )[0]
        )


    def embed_clauses(
        self,
        document_id: str,
        clauses: Sequence[
            ClauseSegment
        ],
        *,
        filename: str | None = None,
    ) -> list[
        ClauseEmbedding
    ]:
        """Generate vector records for classified clauses."""

        document_id = (
            document_id.strip()
        )

        if not document_id:
            raise ValueError(
                "document_id must "
                "not be empty."
            )

        if not clauses:
            return []

        texts = [
            clause.text
            for clause
            in clauses
        ]

        vectors = (
            self.embed_texts(
                texts
            )
        )

        records = []

        for (
            clause,
            vector,
        ) in zip(
            clauses,
            vectors,
        ):

            metadata = {
                "document_id": (
                    document_id
                ),
                "clause_id": (
                    clause.clause_id
                ),
                "clause_type": (
                    clause.clause_type
                ),
                "confidence": (
                    clause.confidence
                ),
                "needs_review": (
                    clause.needs_review
                ),
                "start_char": (
                    clause.start_char
                ),
                "end_char": (
                    clause.end_char
                ),
                "text": (
                    clause.text
                ),
            }

            if filename:
                metadata[
                    "filename"
                ] = filename

            records.append(
                ClauseEmbedding(
                    vector_id=(
                        f"{document_id}:"
                        f"{clause.clause_id}"
                    ),
                    document_id=(
                        document_id
                    ),
                    clause_id=(
                        clause.clause_id
                    ),
                    text=(
                        clause.text
                    ),
                    clause_type=(
                        clause.clause_type
                    ),
                    values=vector,
                    metadata=metadata,
                )
            )

        return records