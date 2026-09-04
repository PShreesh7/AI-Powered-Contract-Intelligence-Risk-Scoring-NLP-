import numpy as np
import pytest

from app.models.schemas import (
    ClauseSegment,
)

from app.search.embeddings import (
    EmbeddingService,
)


class FakeEmbeddingModel:

    def get_sentence_embedding_dimension(
        self,
    ):
        return 3


    def encode(
        self,
        texts,
        *,
        batch_size,
        show_progress_bar,
        convert_to_numpy,
        normalize_embeddings,
    ):

        vectors = []

        for text in texts:

            vector = np.array(
                [
                    float(
                        len(text)
                    ),
                    float(
                        len(
                            text.split()
                        )
                    ),
                    1.0,
                ],
                dtype=np.float32,
            )

            if normalize_embeddings:

                vector = (
                    vector
                    / np.linalg.norm(
                        vector
                    )
                )

            vectors.append(
                vector
            )

        return np.vstack(
            vectors
        )


def make_service():

    return EmbeddingService(
        model=(
            FakeEmbeddingModel()
        ),
        batch_size=2,
    )


def test_embed_text_returns_expected_dimension():

    service = make_service()

    vector = service.embed_text(
        (
            "Either party may "
            "terminate this agreement."
        )
    )

    assert len(vector) == 3

    assert (
        service.dimension
        == 3
    )


def test_embeddings_are_normalized():

    service = make_service()

    vectors = service.embed_texts(
        [
            (
                "This Agreement is "
                "governed by "
                "Delaware law."
            ),
            (
                "Neither party shall "
                "disclose confidential "
                "information."
            ),
        ]
    )

    assert len(vectors) == 2

    for vector in vectors:

        assert (
            np.linalg.norm(
                vector
            )
            == pytest.approx(
                1.0,
                abs=1e-6,
            )
        )


def test_embed_texts_preserves_order():

    service = make_service()

    texts = [
        "short clause",
        (
            "this is a considerably "
            "longer contract clause"
        ),
    ]

    vectors = service.embed_texts(
        texts
    )

    assert (
        vectors[0]
        != vectors[1]
    )

    assert (
        len(vectors)
        == len(texts)
    )


def test_empty_text_is_rejected():

    service = make_service()

    with pytest.raises(
        ValueError,
        match="empty",
    ):
        service.embed_text(
            "   "
        )


def test_embed_clauses_builds_vector_metadata():

    service = make_service()

    clauses = [
        ClauseSegment(
            clause_id="c1",
            text=(
                "This Agreement is "
                "governed by "
                "Delaware law."
            ),
            clause_type=(
                "governing law"
            ),
            confidence=0.92,
            needs_review=False,
            start_char=0,
            end_char=44,
        ),
        ClauseSegment(
            clause_id="c2",
            text=(
                "Either party may "
                "terminate with "
                "thirty days notice."
            ),
            clause_type=(
                "termination"
            ),
            confidence=0.81,
            needs_review=False,
            start_char=45,
            end_char=96,
        ),
    ]

    records = (
        service.embed_clauses(
            "doc-123",
            clauses,
            filename=(
                "sample.pdf"
            ),
        )
    )

    assert len(records) == 2

    assert (
        records[0].vector_id
        == "doc-123:c1"
    )

    assert (
        records[0].document_id
        == "doc-123"
    )

    assert (
        records[0].clause_type
        == "governing law"
    )

    assert (
        records[0]
        .metadata[
            "filename"
        ]
        == "sample.pdf"
    )

    assert (
        records[0]
        .metadata[
            "clause_id"
        ]
        == "c1"
    )

    assert (
        len(
            records[0].values
        )
        == 3
    )


def test_empty_clause_list_returns_empty_records():

    service = make_service()

    assert (
        service.embed_clauses(
            "doc-123",
            [],
        )
        == []
    )


def test_empty_document_id_is_rejected():

    service = make_service()

    with pytest.raises(
        ValueError,
        match="document_id",
    ):
        service.embed_clauses(
            "  ",
            [],
        )