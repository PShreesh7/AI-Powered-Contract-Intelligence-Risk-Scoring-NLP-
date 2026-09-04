from fastapi.testclient import (
    TestClient,
)

import app.main as main_module

from app.models.schemas import (
    ClauseSegment,
    DocumentAnalysis,
)

from app.search.semantic_search import (
    SemanticSearchResult,
)


client = TestClient(
    main_module.app
)


class FakeSemanticSearchService:

    def __init__(
        self,
    ):
        self.deleted = []

        self.index_calls = []

    def search(
        self,
        query,
        *,
        top_k=5,
        document_id=None,
        clause_type=None,
        min_score=None,
        metadata_filter=None,
    ):
        return [
            SemanticSearchResult(
                rank=1,
                vector_id=(
                    "doc-1:c1"
                ),
                score=0.94,
                document_id=(
                    "doc-1"
                ),
                clause_id="c1",
                clause_type=(
                    "termination"
                ),
                text=(
                    "Either party may "
                    "terminate with "
                    "thirty days notice."
                ),
                filename=(
                    "contract.pdf"
                ),
                confidence=0.93,
                needs_review=False,
                start_char=0,
                end_char=62,
                metadata={
                    "document_id": (
                        "doc-1"
                    ),
                    "clause_id": "c1",
                    "clause_type": (
                        "termination"
                    ),
                },
            )
        ]

    def index_clauses(
        self,
        *,
        document_id,
        clauses,
        filename=None,
        batch_size=100,
    ):
        self.index_calls.append(
            {
                "document_id": (
                    document_id
                ),
                "clauses": clauses,
                "filename": filename,
            }
        )

        return len(
            clauses
        )

    def describe_stats(
        self,
    ):
        return {
            "dimension": 384,
            "total_vector_count": 12,
        }

    def delete_document(
        self,
        document_id,
    ):
        self.deleted.append(
            document_id
        )


class FakeAnalysisService:

    def analyze_file(
        self,
        path,
        *,
        filename,
    ):
        return DocumentAnalysis(
            document_id="doc-api-1",
            filename=filename,
            raw_text_length=120,
            entities=[],
            clauses=[
                ClauseSegment(
                    clause_id="c1",
                    text=(
                        "Either party may "
                        "terminate this "
                        "agreement with "
                        "thirty days notice."
                    ),
                    clause_type=(
                        "termination"
                    ),
                    confidence=0.93,
                    needs_review=False,
                    start_char=0,
                    end_char=75,
                )
            ],
            risk_flags=[],
        )


def test_search_query_endpoint(
    monkeypatch,
):

    fake = (
        FakeSemanticSearchService()
    )

    monkeypatch.setattr(
        main_module,
        "_semantic_search_service",
        fake,
    )

    response = client.post(
        "/search/query",
        json={
            "query": (
                "How can the "
                "agreement end?"
            ),
            "top_k": 5,
        },
    )

    assert (
        response.status_code
        == 200
    )

    body = response.json()

    assert (
        body["status"]
        == "success"
    )

    assert (
        body["count"]
        == 1
    )

    assert (
        body["results"][0]
        ["clause_type"]
        == "termination"
    )


def test_search_returns_503_when_unavailable(
    monkeypatch,
):

    monkeypatch.setattr(
        main_module,
        "_semantic_search_service",
        None,
    )

    monkeypatch.setattr(
        main_module,
        "_search_init_error",
        (
            "PINECONE_API_KEY "
            "is not configured."
        ),
    )

    response = client.post(
        "/search/query",
        json={
            "query": (
                "termination"
            )
        },
    )

    assert (
        response.status_code
        == 503
    )


def test_analyze_and_index_endpoint(
    monkeypatch,
):

    fake_search = (
        FakeSemanticSearchService()
    )

    monkeypatch.setattr(
        main_module,
        "_semantic_search_service",
        fake_search,
    )

    monkeypatch.setattr(
        main_module,
        "_contract_analysis_service",
        FakeAnalysisService(),
    )

    response = client.post(
        "/analyze/index",
        files={
            "file": (
                "contract.pdf",
                b"fake-pdf-content",
                "application/pdf",
            )
        },
    )

    assert (
        response.status_code
        == 200
    )

    body = response.json()

    assert (
        body["indexed_count"]
        == 1
    )

    assert (
        body["analysis"]
        ["document_id"]
        == "doc-api-1"
    )

    assert (
        len(
            fake_search
            .index_calls
        )
        == 1
    )


def test_search_stats_endpoint(
    monkeypatch,
):

    monkeypatch.setattr(
        main_module,
        "_semantic_search_service",
        FakeSemanticSearchService(),
    )

    response = client.get(
        "/search/stats"
    )

    assert (
        response.status_code
        == 200
    )

    body = response.json()

    assert (
        body["stats"]
        ["dimension"]
        == 384
    )

    assert (
        body["stats"]
        ["total_vector_count"]
        == 12
    )


def test_delete_document_endpoint(
    monkeypatch,
):

    fake = (
        FakeSemanticSearchService()
    )

    monkeypatch.setattr(
        main_module,
        "_semantic_search_service",
        fake,
    )

    response = client.delete(
        (
            "/search/documents/"
            "doc-1"
        )
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        fake.deleted
        == ["doc-1"]
    )