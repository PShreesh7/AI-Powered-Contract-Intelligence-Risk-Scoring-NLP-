import io
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.models.schemas import ClauseSegment, ExtractedEntity
from app.qa.contract_qa import QAUnavailableError


class DummyExtractor:
    def extract(self, text: str):
        return [
            ExtractedEntity(
                label="PARTY",
                text="Acme Corp",
                start_char=0,
                end_char=9,
                confidence=1.0,
            )
        ]


class DummyClassifier:
    def classify(self, clauses, offsets):
        results = []
        for i, (clause, (start, end)) in enumerate(zip(clauses, offsets)):
            results.append(
                ClauseSegment(
                    clause_id=f"clause_{i}",
                    text=clause,
                    clause_type="termination",
                    confidence=0.92,
                    needs_review=False,
                    start_char=start,
                    end_char=end,
                )
            )
        return results


from app.services.contract_analysis import ContractAnalysisService


@pytest.fixture
def client():
    # Inject dummy models so unit tests are fast and don't download/load BART
    orig_ext = main_module._entity_extractor
    orig_clf = main_module._clause_classifier
    orig_svc = main_module._contract_analysis_service

    dummy_ext = DummyExtractor()
    dummy_clf = DummyClassifier()
    main_module._entity_extractor = dummy_ext
    main_module._clause_classifier = dummy_clf
    main_module._contract_analysis_service = ContractAnalysisService(
        entity_extractor=dummy_ext,
        clause_classifier=dummy_clf,
    )

    yield TestClient(main_module.app)

    main_module._entity_extractor = orig_ext
    main_module._clause_classifier = orig_clf
    main_module._contract_analysis_service = orig_svc


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    assert res.json()["analysis_ready"] is True


def test_ask_endpoint_success(client):
    with patch("app.main.ask_question", return_value="Termination requires 30 days notice."):
        res = client.post(
            "/ask",
            json={
                "question": "What is the notice period?",
                "clause_texts": ["Either party may terminate upon 30 days written notice."],
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert "30 days" in data["answer"]


def test_ask_endpoint_missing_api_key(client):
    with patch("app.main.ask_question", side_effect=QAUnavailableError("No GOOGLE_API_KEY set.")):
        res = client.post(
            "/ask",
            json={
                "question": "What is the notice period?",
                "clause_texts": ["Clause text."],
            },
        )
        assert res.status_code == 503
        assert "No GOOGLE_API_KEY set" in res.json()["detail"]


def test_ask_endpoint_empty_clauses(client):
    res = client.post(
        "/ask",
        json={
            "question": "What is this?",
            "clause_texts": [],
        },
    )
    assert res.status_code == 400


def test_ask_endpoint_empty_question(client):
    res = client.post(
        "/ask",
        json={
            "question": "   ",
            "clause_texts": ["Some clause."],
        },
    )
    assert res.status_code == 400


def test_analyze_docx_file(client):
    file_path = "data/sample_contracts/Sample_Consulting_NDA_Agreement.docx"
    with open(file_path, "rb") as f:
        res = client.post(
            "/analyze",
            files={"file": ("Sample_Consulting_NDA_Agreement.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    analysis = data["analysis"]
    assert analysis["filename"] == "Sample_Consulting_NDA_Agreement.docx"
    assert len(analysis["clauses"]) > 0
    assert len(analysis["entities"]) > 0


def test_export_pdf_report(client):
    file_path = "data/sample_contracts/Sample_Consulting_NDA_Agreement.docx"
    with open(file_path, "rb") as f:
        res = client.post(
            "/analyze/pdf-report",
            files={"file": ("Sample_Consulting_NDA_Agreement.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        )
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert "attachment; filename=" in res.headers["content-disposition"]
    assert res.content.startswith(b"%PDF-")


def test_static_root_serving(client):
    res = client.get("/")
    # If dist/index.html exists, returns 200 with html
    if main_module.dist_dir.exists():
        assert res.status_code == 200
        assert "LexAI" in res.text or "<!doctype html>" in res.text
