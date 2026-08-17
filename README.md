# Legal contract intelligence platform

An NLP platform for legal/compliance teams that ingests contracts (PDF/DOCX),
extracts key entities (dates, parties, jurisdictions), classifies clause
(termination, confidentiality, indemnification, etc.), and flags anomalous
or high-risk clause language.

See `docs/ARCHITECTURE.md` for the full pipeline design and
`docs/COMMIT_PLAN.md` for the 5-day team build plan.

## Setup

```bash
python -m venv venv
source venv/bin/activate  venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Run the API

```bash
uvicorn app.main:app --reload
```

Then test it:

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -F "file=@data/sample_contracts/sample.pdf"
```

## Run tests

```bash
pytest
```

## Project structure

```
app/
  ingestion/     PDF/DOCX text extraction
  utils/          text cleaning + clause segmentation
  ner/            entity extraction (dates, parties, jurisdictions)
  clauses/        clause type classification
  risk/           rule-based + LLM-based risk flagging
  models/         shared Pydantic schemas
  main.py         FastAPI app / /analyze endpoint
tests/            unit + integration tests
docs/             architecture notes + team commit plan
```

## Status

Early-stage scaffold. NER runs on spaCy's base model, clause classification
uses zero-shot (`facebook/bart-large-mnli`), risk flagging combines rule-based
heuristics with a pluggable LLM scoring layer. See `docs/ARCHITECTURE.md` for
the upgrade path (fine-tuning, vector search, async processing, frontend).
