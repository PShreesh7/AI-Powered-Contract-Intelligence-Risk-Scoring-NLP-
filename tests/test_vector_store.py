from types import SimpleNamespace

import pytest

from app.search.embeddings import (
    ClauseEmbedding,
)

from app.search.vector_store import (
    PineconeVectorStore,
)


class FakeIndex:

    def __init__(
        self,
    ):
        self.upsert_calls = []
        self.query_calls = []
        self.delete_calls = []

    def upsert(
        self,
        **kwargs,
    ):
        self.upsert_calls.append(
            kwargs
        )

        return {
            "upserted_count": len(
                kwargs["vectors"]
            )
        }

    def query(
        self,
        **kwargs,
    ):
        self.query_calls.append(
            kwargs
        )

        return {
            "matches": [
                {
                    "id": (
                        "doc-1:c1"
                    ),
                    "score": 0.91,
                    "metadata": {
                        "document_id": (
                            "doc-1"
                        ),
                        "clause_id": "c1",
                        "clause_type": (
                            "termination"
                        ),
                        "text": (
                            "Either party "
                            "may terminate."
                        ),
                    },
                },
                {
                    "id": (
                        "doc-2:c2"
                    ),
                    "score": 0.82,
                    "metadata": {
                        "document_id": (
                            "doc-2"
                        ),
                        "clause_id": "c2",
                        "clause_type": (
                            "termination"
                        ),
                        "text": (
                            "Termination "
                            "requires notice."
                        ),
                    },
                },
            ]
        }

    def delete(
        self,
        **kwargs,
    ):
        self.delete_calls.append(
            kwargs
        )

    def describe_index_stats(
        self,
    ):
        return {
            "dimension": 3,
            "total_vector_count": 2,
        }


def make_store():

    return PineconeVectorStore(
        client=object(),
        index=FakeIndex(),
        dimension=3,
    )


def make_embedding(
    *,
    vector_id="doc-1:c1",
):

    return ClauseEmbedding(
        vector_id=vector_id,
        document_id="doc-1",
        clause_id="c1",
        text=(
            "Either party may "
            "terminate this agreement."
        ),
        clause_type="termination",
        values=[
            0.1,
            0.2,
            0.3,
        ],
        metadata={
            "document_id": "doc-1",
            "clause_id": "c1",
            "clause_type": (
                "termination"
            ),
            "text": (
                "Either party may "
                "terminate this agreement."
            ),
        },
    )


def test_upsert_embeddings():

    store = make_store()

    count = (
        store.upsert_embeddings(
            [
                make_embedding()
            ]
        )
    )

    assert count == 1

    call = (
        store._index
        .upsert_calls[0]
    )

    assert (
        call["namespace"]
        == "contracts"
    )

    assert (
        call["vectors"][0]["id"]
        == "doc-1:c1"
    )

    assert (
        call["vectors"][0]
        ["values"]
        == [
            0.1,
            0.2,
            0.3,
        ]
    )


def test_empty_upsert_returns_zero():

    store = make_store()

    assert (
        store
        .upsert_embeddings([])
        == 0
    )


def test_query_returns_normalized_matches():

    store = make_store()

    matches = store.query(
        [
            0.1,
            0.2,
            0.3,
        ],
        top_k=2,
    )

    assert len(matches) == 2

    assert (
        matches[0].vector_id
        == "doc-1:c1"
    )

    assert (
        matches[0].score
        == pytest.approx(
            0.91
        )
    )

    assert (
        matches[0]
        .metadata[
            "clause_type"
        ]
        == "termination"
    )


def test_query_builds_metadata_filter():

    store = make_store()

    store.query(
        [
            0.1,
            0.2,
            0.3,
        ],
        document_id="doc-1",
        clause_type=(
            "termination"
        ),
    )

    call = (
        store._index
        .query_calls[0]
    )

    assert call["filter"] == {
        "$and": [
            {
                "document_id": {
                    "$eq": "doc-1"
                }
            },
            {
                "clause_type": {
                    "$eq": (
                        "termination"
                    )
                }
            },
        ]
    }


def test_delete_document_uses_metadata_filter():

    store = make_store()

    store.delete_document(
        "doc-1"
    )

    call = (
        store._index
        .delete_calls[0]
    )

    assert call == {
        "filter": {
            "document_id": {
                "$eq": "doc-1"
            }
        },
        "namespace": (
            "contracts"
        ),
    }


def test_wrong_vector_dimension_is_rejected():

    store = make_store()

    with pytest.raises(
        ValueError,
        match=(
            "dimension mismatch"
        ),
    ):
        store.query(
            [
                0.1,
                0.2,
            ]
        )


def test_invalid_top_k_is_rejected():

    store = make_store()

    with pytest.raises(
        ValueError,
        match="top_k",
    ):
        store.query(
            [
                0.1,
                0.2,
                0.3,
            ],
            top_k=0,
        )