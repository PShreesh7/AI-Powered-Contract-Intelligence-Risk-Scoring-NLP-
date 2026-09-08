"""
CLI Script to execute the full Legal NLP Intelligence model pipeline.
Usage:
    python run_model.py
    python run_model.py data/sample_contracts/Sample_Consulting_NDA_Agreement.docx
"""
import sys
import os
from pathlib import Path

# Fix Windows console encoding for Unicode legal symbols
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import httpx
from app.ner.entity_extractor import EntityExtractor
from app.clauses.clause_classifier import classifier_from_environment
from app.services.contract_analysis import ContractAnalysisService
from app.qa.contract_qa import ask_question
from app.models.schemas import DocumentAnalysis, ExtractedEntity, ClauseSegment, RiskFlag

def run(contract_path_str: str = None):
    if not contract_path_str:
        contract_path_str = "data/sample_contracts/Sample_Master_Service_Agreement.pdf"

    contract_path = Path(contract_path_str)
    if not contract_path.exists():
        print(f"Error: Contract file '{contract_path}' not found.", flush=True)
        sys.exit(1)

    print("=" * 72, flush=True)
    print("        LEXAI CONTRACT INTELLIGENCE - MODEL INFERENCE RUNNER       ", flush=True)
    print("=" * 72, flush=True)
    print(f"Target Contract : {contract_path.name}", flush=True)
    print(f"Path            : {contract_path.resolve()}", flush=True)

    # Check if backend server is available for fast warm inference
    server_online = False
    try:
        r = httpx.get("http://127.0.0.1:8000/health", timeout=1.5)
        server_online = (r.status_code == 200 and r.json().get("analysis_ready", False))
    except Exception:
        server_online = False

    if server_online:
        print("Connected to warm FastAPI backend (http://127.0.0.1:8000).", flush=True)
        print("Executing contract analysis model pipeline...", flush=True)
        with open(contract_path, "rb") as f:
            mime = "application/pdf" if contract_path.suffix.lower() == ".pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            resp = httpx.post(
                "http://127.0.0.1:8000/analyze",
                files={"file": (contract_path.name, f, mime)},
                timeout=120.0
            )
        resp.raise_for_status()
        analysis = DocumentAnalysis(**resp.json()["analysis"])
    else:
        print("Backend offline; running direct local pipeline...", flush=True)
        print("Initializing NLP models (spaCy NER, Zero-Shot/Legal-BERT)...", flush=True)
        extractor = EntityExtractor()
        classifier = classifier_from_environment()
        service = ContractAnalysisService(extractor, classifier)
        print("Processing document through pipeline...", flush=True)
        analysis = service.analyze_file(str(contract_path), filename=contract_path.name)

    print("\n" + "-" * 72)
    print("1. DOCUMENT SUMMARY & PIPELINE METRICS")
    print("-" * 72)
    print(f"Document ID        : {analysis.document_id}")
    print(f"Characters Analyzed: {analysis.raw_text_length:,}")
    print(f"Clauses Segmented  : {len(analysis.clauses)}")
    print(f"Entities Extracted : {len(analysis.entities)}")
    print(f"Risk Flags Found   : {len(analysis.risk_flags)}")

    print("\n" + "-" * 72)
    print("2. EXTRACTED LEGAL ENTITIES (NER)")
    print("-" * 72)
    if analysis.entities:
        for e in analysis.entities[:12]:
            conf_str = f"({e.confidence:.2f})" if e.confidence else ""
            print(f"  [{e.label:<14}] {e.text:<36} {conf_str}")
    else:
        print("  No named entities detected.")

    print("\n" + "-" * 72)
    print("3. CLASSIFIED CONTRACT CLAUSES")
    print("-" * 72)
    for i, c in enumerate(analysis.clauses[:8], 1):
        status = "[NEEDS REVIEW]" if c.needs_review else "[CONFIDENT]"
        print(f"  Clause {i:02d} | {c.clause_type.upper():<24} (Conf: {c.confidence:.2f}) {status}")
        preview = c.text.replace("\n", " ").strip()
        if len(preview) > 95:
            preview = preview[:95] + "..."
        print(f"            \"{preview}\"")

    if len(analysis.clauses) > 8:
        print(f"  ... and {len(analysis.clauses) - 8} more clauses classified.")

    print("\n" + "-" * 72)
    print("4. RISK DETECTION & AI REMEDIATION")
    print("-" * 72)
    if analysis.risk_flags:
        for i, f in enumerate(analysis.risk_flags, 1):
            badge = f"[{f.risk_level.upper()}]"
            print(f"  {badge:<8} Rule: {f.reason}")
            if f.suggestion:
                print(f"           Tip:  {f.suggestion}")
    else:
        print("  ✓ No high-risk or non-standard provisions flagged in this contract.")

    print("\n" + "-" * 72)
    print("5. GEMINI AI CONTRACT Q&A INFERENCE")
    print("-" * 72)
    clause_texts = [c.text for c in analysis.clauses]
    test_question = "What are the termination conditions, notice period, and governing law?"
    print(f"  Question: {test_question}")
    try:
        answer = ask_question(clause_texts, test_question)
        print(f"\n  AI Answer:\n  {answer}")
    except Exception as exc:
        print(f"  AI Q&A Error: {exc}")

    print("\n" + "=" * 72)
    print("               MODEL INFERENCE COMPLETED SUCCESSFULLY               ")
    print("=" * 72)

if __name__ == "__main__":
    path_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run(path_arg)
