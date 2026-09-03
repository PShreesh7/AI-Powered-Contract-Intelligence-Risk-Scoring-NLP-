import pytest

from app.models.schemas import (
    ClauseSegment,
)

from app.search.embeddings import (
    ClauseEmbedding,
)

from app.search.semantic_search import (
    SemanticSearchService,
)

from app.search.vector_store import (
    VectorSearchMatch,
)


class FakeEmbeddingService:

    dimension = 3

    def __init__(
        self,
    ):
        self.embed_text_calls = []
        self.embed_clause_calls = []

    def embed_text(
        self,
        text,
    ):
        self.embed_text_calls.append(
            text
        )

        return [
            0.1,
            0.2,
            0.3,
        ]

    def embed_clauses(
        self,
        document_id,
        clauses,
        *,
        filename=None,
    ):
        self.embed_clause_calls.append(
            {
                "document_id": (
                    document_id
                ),
                "clauses": clauses,
                "filename": filename,
            }
        )

        records = []

        for clause in clauses:

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
                    text=clause.text,
                    clause_type=(
                        clause.clause_type
                    ),
                    values=[
                        0.1,
                        0.2,
                        0.3,
                    ],
                    metadata={
                        "document_id": (
                            document_id
                        ),
                        "clause_id": (
                            clause.clause_id
                        ),
                        "clause_type": (
                            clause
                            .clause_type
                        ),
                        "text": (
                            clause.text
                        ),
                        "confidence": (
                            clause
                            .confidence
                        ),
                        "needs_review": (
                            clause
                            .needs_review
                        ),
                        "start_char": (
                            clause
                            .start_char
                        ),
                        "end_char": (
                            clause
                            .end_char
                        ),
                        "filename": (
                            filename
                        ),
                    },
                )
            )

        return records


class FakeVectorStore:

    dimension = 3

    def __init__(
        self,
    ):
        self.upsert_calls = []
        self.query_calls = []
        self.delete_calls = []

    def upsert_embeddings(
        self,
        records,
        *,
        batch_size=100,
    ):
        self.upsert_calls.append(
            {
                "records": records,
                "batch_size": (
                    batch_size
                ),
            }
        )

        return len(
            records
        )

    def query(
        self,
        vector,
        *,
        top_k=5,
        document_id=None,
        clause_type=None,
        metadata_filter=None,
    ):
        self.query_calls.append(
            {
                "vector": vector,
                "top_k": top_k,
                "document_id": (
                    document_id
                ),
                "clause_type": (
                    clause_type
                ),
                "metadata_filter": (
                    metadata_filter
                ),
            }
        )

        return [
            VectorSearchMatch(
                vector_id=(
                    "doc-1:c1"
                ),
                score=0.93,
                metadata={
                    "document_id": (
                        "doc-1"
                    ),
                    "clause_id": "c1",
                    "clause_type": (
                        "termination"
                    ),
                    "text": (
                        "Either party "
                        "may terminate "
                        "this agreement "
                        "with thirty "
                        "days notice."
                    ),
                    "filename": (
                        "contract.pdf"
                    ),
                    "confidence": 0.94,
                    "needs_review": (
                        False
                    ),
                    "start_char": 10,
                    "end_char": 81,
                },
            ),
            VectorSearchMatch(
                vector_id=(
                    "doc-2:c2"
                ),
                score=0.71,
                metadata={
                    "document_id": (
                        "doc-2"
                    ),
                    "clause_id": "c2",
                    "clause_type": (
                        "termination"
                    ),
                    "text": (
                        "Termination "
                        "requires "
                        "written notice."
                    ),
                    "confidence": 0.80,
                    "needs_review": (
                        False
                    ),
                    "start_char": 20,
                    "end_char": 56,
                },
            ),
        ]

    def delete_document(
        self,
        document_id,
    ):
        self.delete_calls.append(
            document_id
        )

    def describe_stats(
        self,
    ):
        return {
            "dimension": 3,
            "total_vector_count": 2,
        }


def make_service():

    return SemanticSearchService(
        embedding_service=(
            FakeEmbeddingService()
        ),
        vector_store=(
            FakeVectorStore()
        ),
    )


def make_clause():

    return ClauseSegment(
        clause_id="c1",
        text=(
            "Either party may "
            "terminate this agreement "
            "with thirty days notice."
        ),
        clause_type="termination",
        confidence=0.94,
        needs_review=False,
        start_char=10,
        end_char=81,
    )


def test_index_clauses():

    service = make_service()

    count = service.index_clauses(
        document_id="doc-1",
        clauses=[
            make_clause()
        ],
        filename=(
            "contract.pdf"
        ),
    )

    assert count == 1

    assert (
        len(
            service
            .vector_store
            .upsert_calls
        )
        == 1
    )

    call = (
        service.vector_store
        .upsert_calls[0]
    )

    assert (
        call["records"][0]
        .vector_id
        == "doc-1:c1"
    )


def test_search_embeds_query():

    service = make_service()

    service.search(
        (
            "How can this "
            "agreement be "
            "terminated?"
        ),
        top_k=2,
    )

    assert (
        service
        .embedding_service
        .embed_text_calls
        == [
            (
                "How can this "
                "agreement be "
                "terminated?"
            )
        ]
    )


def test_search_passes_filters():

    service = make_service()

    service.search(
        "termination clause",
        top_k=3,
        document_id="doc-1",
        clause_type=(
            "termination"
        ),
    )

    call = (
        service.vector_store
        .query_calls[0]
    )

    assert (
        call["top_k"]
        == 3
    )

    assert (
        call["document_id"]
        == "doc-1"
    )

    assert (
        call["clause_type"]
        == "termination"
    )


def test_search_returns_ranked_results():

    service = make_service()

    results = service.search(
        (
            "How can the "
            "contract be "
            "terminated?"
        )
    )

    assert len(
        results
    ) == 2

    assert (
        results[0].rank
        == 1
    )

    assert (
        results[0].score
        == pytest.approx(
            0.93
        )
    )

    assert (
        results[0]
        .document_id
        == "doc-1"
    )

    assert (
        results[0]
        .clause_type
        == "termination"
    )

    assert (
        results[0]
        .filename
        == "contract.pdf"
    )


def test_min_score_filters_results():

    service = make_service()

    results = service.search(
        "termination",
        min_score=0.80,
    )

    assert (
        len(results)
        == 1
    )

    assert (
        results[0].score
        == pytest.approx(
            0.93
        )
    )


def test_empty_query_is_rejected():

    service = make_service()

    with pytest.raises(
        ValueError,
        match="query",
    ):
        service.search(
            "   "
        )


def test_invalid_top_k_is_rejected():

    service = make_service()

    with pytest.raises(
        ValueError,
        match="top_k",
    ):
        service.search(
            "termination",
            top_k=0,
        )


def test_empty_clause_collection_returns_zero():

    service = make_service()

    count = service.index_clauses(
        document_id="doc-1",
        clauses=[],
    )

    assert count == 0


def test_delete_document():

    service = make_service()

    service.delete_document(
        "doc-1"
    )

    assert (
        service
        .vector_store
        .delete_calls
        == ["doc-1"]
    )


def test_dimension_mismatch_is_rejected():

    embedding_service = (
        FakeEmbeddingService()
    )

    vector_store = (
        FakeVectorStore()
    )

    vector_store.dimension = 384

    with pytest.raises(
        ValueError,
        match=(
            "dimension"
        ),
    ):
        SemanticSearchService(
            embedding_service=(
                embedding_service
            ),
            vector_store=(
                vector_store
            ),
        )