# Legal Contract Intelligence Platform

An NLP-based platform for analyzing legal contracts and identifying information that may require further review. The system ingests PDF/DOCX documents, extracts key entities, classifies contractual clauses, and flags potentially anomalous or high-risk language.

## Problem

Manual contract review is time-consuming, especially for lengthy documents. Important clauses, entities, and risk indicators can be difficult to identify consistently.

## Approach

The platform processes a contract through the following pipeline:

```text
PDF / DOCX
    ↓
Text Extraction & Cleaning
    ↓
Clause Segmentation
    ↓
Entity Extraction
    ↓
Clause Classification
    ↓
Risk Analysis
    ↓
Structured Response
```

It combines **spaCy NER, transformer-based zero-shot classification, and rule-based/LLM-assisted risk analysis**.

## Key Features

* PDF/DOCX text extraction
* Entity extraction for parties, dates, and jurisdictions
* Clause classification for areas such as termination, confidentiality, and indemnification
* Rule-based risk detection
* Pluggable LLM-based risk analysis
* FastAPI `/analyze` endpoint
* Pydantic-based data models
* Automated tests with Pytest

## Tech Stack

**Python · FastAPI · spaCy · Hugging Face Transformers · BART/MNLI · Pydantic · Pytest**

## Project Structure

```text
app/
├── ingestion/     # PDF/DOCX text extraction
├── utils/         # Text cleaning and clause segmentation
├── ner/           # Entity extraction
├── clauses/       # Clause classification
├── risk/          # Risk analysis
├── models/        # Pydantic schemas
└── main.py        # FastAPI application

tests/             # Unit and integration tests
data/              # Sample contracts
docs/              # Architecture documentation
```

## Setup

### 1. Create virtual environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Run the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Example request:

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -F "file=@data/sample_contracts/sample.pdf"
```

## Run Tests

```bash
pytest
```

## What Makes It Different

The system goes beyond simple keyword matching by combining **clause-level analysis, named entity recognition, semantic classification, and risk detection**. Its modular design also allows individual NLP or risk-analysis components to be improved independently.

## Future Scope

* Fine-tuned legal-domain NLP models
* RAG-based legal knowledge retrieval
* Contract comparison and change detection
* Improved risk scoring
* Web-based dashboard
* Scalable asynchronous processing

## Status

**Working prototype** with modular NLP, clause classification, and risk-analysis components. The architecture is designed to support further model improvements and production-oriented features.

## Disclaimer

This project is intended for educational and internship purposes. It provides AI-assisted contract analysis and should not be treated as legal advice or a substitute for professional legal review.
