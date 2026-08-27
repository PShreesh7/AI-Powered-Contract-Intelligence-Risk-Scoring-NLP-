"""
Day 5 module: API layer. Ties ingestion -> NER -> clause classification ->
risk flagging into a single /analyze endpoint.

Run locally with:
    uvicorn app.main:app --reload
"""
from __future__ import annotations
import os
import shutil
import tempfile
import uuid

class QuestionRequest(BaseModel):
    question: str
    clause_texts: list[str]

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import Response
from app.reports.pdf_report import generate_pdf_report
from app.qa.contract_qa import ask_question, QAUnavailableError
from pydantic import BaseModel 


from app.ingestion.parser import extract_text, UnsupportedFileTypeError
from app.utils.text_utils import clean_text, split_into_clauses
from app.ner.entity_extractor import EntityExtractor
from app.clauses.clause_classifier import ClauseClassifier
from app.risk.risk_flagger import flag_risks
from app.models.schemas import DocumentAnalysis, AnalyzeResponse, ClauseSegment

app = FastAPI(title="Legal Contract Intelligence API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this before deploying
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
    _clause_classifier = ClauseClassifier()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_contract(file: UploadFile = File(...)):
    if _entity_extractor is None or _clause_classifier is None:
        raise HTTPException(status_code=503, detail="Models still loading, try again shortly.")

    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        raw_text = extract_text(tmp_path)
    except UnsupportedFileTypeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        os.remove(tmp_path)

    text = clean_text(raw_text)
    entities = _entity_extractor.extract(text)

    clause_texts = split_into_clauses(text)
    # naive offset tracking -- good enough for v1, refine if you need exact spans
    offsets = []
    cursor = 0
    for c in clause_texts:
        start = text.find(c, cursor)
        start = start if start != -1 else cursor
        end = start + len(c)
        offsets.append((start, end))
        cursor = end

    clauses = _clause_classifier.classify(clause_texts, offsets)
    risk_flags = flag_risks(clauses)

    analysis = DocumentAnalysis(
        document_id=str(uuid.uuid4()),
        filename=file.filename,
        raw_text_length=len(text),
        entities=entities,
        clauses=clauses,
        risk_flags=risk_flags,
    )

    return AnalyzeResponse(status="success", analysis=analysis)
