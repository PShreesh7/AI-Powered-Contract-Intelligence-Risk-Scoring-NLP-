from __future__ import annotations

import os
import shutil
import tempfile

from dataclasses import (
    asdict,
)

from typing import (
    Any,
)

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile,
)

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.clauses.clause_classifier import (
    classifier_from_environment,
)

from app.ingestion.parser import (
    UnsupportedFileTypeError,
)

from app.models.schemas import (
    AnalyzeAndIndexResponse,
    AnalyzeResponse,
    SearchStatsResponse,
    SemanticSearchHit,
    SemanticSearchRequest,
    SemanticSearchResponse,
)

from app.ner.entity_extractor import (
    EntityExtractor,
)

from app.search.embeddings import (
    EmbeddingService,
)

from app.search.semantic_search import (
    SemanticSearchService,
)

from app.search.vector_store import (
    vector_store_from_environment,
)

from app.services.contract_analysis import (
    ContractAnalysisService,
)


app = FastAPI(
    title=(
        "Legal Contract "
        "Intelligence API"
    ),
    version="0.2.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


_entity_extractor = None

_clause_classifier = None

_contract_analysis_service = None

_semantic_search_service = None

_search_init_error = None


@app.on_event(
    "startup"
)
def load_models():
    """Load expensive NLP resources once."""
    global contract_analyzer, vector_store, embedding_model
    # global (
    #     _entity_extractor,
    #     _clause_classifier,
    #     _contract_analysis_service,
    #     _semantic_search_service,
    #     _search_init_error,
    # )

    _entity_extractor = (
        EntityExtractor()
    )

    _clause_classifier = (
        classifier_from_environment()
    )

    _contract_analysis_service = (
        ContractAnalysisService(
            entity_extractor=(
                _entity_extractor
            ),
            clause_classifier=(
                _clause_classifier
            ),
        )
    )

    _semantic_search_service = None

    _search_init_error = None

    pinecone_api_key = os.getenv(
        "PINECONE_API_KEY"
    )

    if not pinecone_api_key:
        _search_init_error = (
            "PINECONE_API_KEY "
            "is not configured."
        )

        return

    try:
        embedding_service = (
            EmbeddingService()
        )

        vector_store = (
            vector_store_from_environment(
                dimension=(
                    embedding_service
                    .dimension
                ),
                auto_create=True,
            )
        )

        _semantic_search_service = (
            SemanticSearchService(
                embedding_service=(
                    embedding_service
                ),
                vector_store=(
                    vector_store
                ),
            )
        )

    except Exception as exc:
        _search_init_error = (
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        _semantic_search_service = None


def _require_analysis_service():
    if (
        _contract_analysis_service
        is None
    ):
        raise HTTPException(
            status_code=503,
            detail=(
                "Contract analysis "
                "models are not "
                "loaded yet."
            ),
        )

    return (
        _contract_analysis_service
    )


def _require_search_service():
    if (
        _semantic_search_service
        is None
    ):
        detail = (
            "Semantic search is "
            "not available."
        )

        if _search_init_error:
            detail += (
                " "
                + _search_init_error
            )

        raise HTTPException(
            status_code=503,
            detail=detail,
        )

    return (
        _semantic_search_service
    )


async def _analyze_uploaded_file(
    file: UploadFile,
):
    """Persist an upload temporarily and run contract analysis."""

    analysis_service = (
        _require_analysis_service()
    )

    filename = (
        file.filename
        or "contract"
    )

    suffix = os.path.splitext(
        filename
    )[1]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as tmp:

        shutil.copyfileobj(
            file.file,
            tmp,
        )

        tmp_path = tmp.name

    try:
        return (
            analysis_service
            .analyze_file(
                tmp_path,
                filename=filename,
            )
        )

    except UnsupportedFileTypeError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(
                exc
            ),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(
                exc
            ),
        ) from exc

    finally:
        if os.path.exists(
            tmp_path
        ):
            os.remove(
                tmp_path
            )


def _serialize_stats(
    stats: Any,
) -> dict[
    str,
    Any,
]:
    """Normalize Pinecone SDK stats into JSON-safe data."""

    if isinstance(
        stats,
        dict,
    ):
        return stats

    to_dict = getattr(
        stats,
        "to_dict",
        None,
    )

    if callable(
        to_dict
    ):
        return dict(
            to_dict()
        )

    model_dump = getattr(
        stats,
        "model_dump",
        None,
    )

    if callable(
        model_dump
    ):
        return dict(
            model_dump()
        )

    return {
        "value": str(
            stats
        )
    }


@app.get(
    "/health"
)
def health():
    return {
        "status": "ok",
        "analysis_ready": (
            _contract_analysis_service
            is not None
        ),
        "semantic_search_ready": (
            _semantic_search_service
            is not None
        ),
        "semantic_search_error": (
            _search_init_error
        ),
    }


@app.post(
    "/analyze",
    response_model=(
        AnalyzeResponse
    ),
)
async def analyze_contract(
    file: UploadFile = File(...),
):
    analysis = (
        await _analyze_uploaded_file(
            file
        )
    )

    return AnalyzeResponse(
        status="success",
        analysis=analysis,
    )


@app.post(
    "/analyze/index",
    response_model=(
        AnalyzeAndIndexResponse
    ),
)
async def analyze_and_index_contract(
    file: UploadFile = File(...),
):
    """Analyze an uploaded contract and index its clauses."""

    search_service = (
        _require_search_service()
    )

    analysis = (
        await _analyze_uploaded_file(
            file
        )
    )

    try:
        indexed_count = (
            search_service
            .index_clauses(
                document_id=(
                    analysis
                    .document_id
                ),
                clauses=(
                    analysis.clauses
                ),
                filename=(
                    analysis.filename
                ),
            )
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Contract analysis "
                "succeeded, but vector "
                "indexing failed: "
                f"{exc}"
            ),
        ) from exc

    return AnalyzeAndIndexResponse(
        status="success",
        analysis=analysis,
        indexed_count=(
            indexed_count
        ),
    )


@app.post(
    "/search/query",
    response_model=(
        SemanticSearchResponse
    ),
)
def semantic_search(
    request: SemanticSearchRequest,
):
    """Search indexed legal clauses using natural language."""

    search_service = (
        _require_search_service()
    )

    try:
        results = (
            search_service.search(
                request.query,
                top_k=(
                    request.top_k
                ),
                document_id=(
                    request
                    .document_id
                ),
                clause_type=(
                    request
                    .clause_type
                ),
                min_score=(
                    request
                    .min_score
                ),
                metadata_filter=(
                    request
                    .metadata_filter
                ),
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(
                exc
            ),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Semantic search "
                "failed: "
                f"{exc}"
            ),
        ) from exc

    hits = [
        SemanticSearchHit(
            **asdict(
                result
            )
        )
        for result
        in results
    ]

    return SemanticSearchResponse(
        status="success",
        query=request.query,
        count=len(
            hits
        ),
        results=hits,
    )


@app.get(
    "/search/stats",
    response_model=(
        SearchStatsResponse
    ),
)
def search_stats():
    """Return vector-index statistics."""

    search_service = (
        _require_search_service()
    )

    try:
        stats = (
            search_service
            .describe_stats()
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to retrieve "
                "vector index stats: "
                f"{exc}"
            ),
        ) from exc

    return SearchStatsResponse(
        status="success",
        stats=(
            _serialize_stats(
                stats
            )
        ),
    )


@app.delete(
    "/search/documents/{document_id}"
)
def delete_indexed_document(
    document_id: str,
):
    """Remove all vectors belonging to one indexed document."""

    search_service = (
        _require_search_service()
    )

    document_id = (
        document_id.strip()
    )

    if not document_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "document_id must "
                "not be empty."
            ),
        )

    try:
        search_service.delete_document(
            document_id
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to delete "
                "indexed document: "
                f"{exc}"
            ),
        ) from exc

    return {
        "status": "success",
        "document_id": (
            document_id
        ),
        "message": (
            "Indexed document "
            "deleted."
        ),
    }