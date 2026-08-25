from __future__ import annotations

import os
import shutil
import tempfile
import uuid

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
    extract_text,
)

from app.models.schemas import (
    AnalyzeResponse,
    DocumentAnalysis,
)

from app.ner.entity_extractor import (
    EntityExtractor,
)

from app.risk.risk_flagger import (
    flag_risks,
)

from app.utils.text_utils import (
    clean_text,
    split_into_clauses,
)


app = FastAPI(
    title="Legal Contract Intelligence API",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models once at startup -- these are heavy, don't reload per-request
_entity_extractor: EntityExtractor | None = None
_clause_classifier: ClauseClassifier | None = None


@app.on_event("startup")
def load_models():
    global _entity_extractor, _clause_classifier

    _entity_extractor = EntityExtractor()

    _clause_classifier = classifier_from_environment()


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post(
    "/analyze",
    response_model=AnalyzeResponse,
)
async def analyze_contract(
    file: UploadFile = File(...),
):
    if (
        _entity_extractor is None
        or _clause_classifier is None
    ):
        raise HTTPException(
            status_code=503,
            detail="Models are not loaded yet.",
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
        raw_text = extract_text(
            tmp_path
        )

    except UnsupportedFileTypeError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    finally:
        if os.path.exists(
            tmp_path
        ):
            os.remove(
                tmp_path
            )

    text = clean_text(
        raw_text
    )

    entities = (
        _entity_extractor.extract(
            text
        )
    )

    clause_texts = (
        split_into_clauses(
            text
        )
    )

    offsets = []

    cursor = 0

    for clause in clause_texts:
        start = text.find(
            clause,
            cursor,
        )

        if start == -1:
            start = cursor

        end = (
            start
            + len(clause)
        )

        offsets.append(
            (
                start,
                end,
            )
        )

        cursor = end

    clauses = (
        _clause_classifier.classify(
            clause_texts,
            offsets,
        )
    )

    risk_flags = (
        flag_risks(
            clauses
        )
    )

    analysis = DocumentAnalysis(
        document_id=str(
            uuid.uuid4()
        ),
        filename=filename,
        raw_text_length=len(
            text
        ),
        entities=entities,
        clauses=clauses,
        risk_flags=risk_flags,
    )

    return AnalyzeResponse(status="success", analysis=analysis)
