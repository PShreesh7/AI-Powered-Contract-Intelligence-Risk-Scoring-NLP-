# Architecture

## Pipeline

```
Upload (PDF/DOCX)
    -> Ingestion (app/ingestion/parser.py)          extract raw text
    -> Preprocessing (app/utils/text_utils.py)      clean + split into clauses
    -> NER (app/ner/entity_extractor.py)            dates, parties, jurisdictions
    -> Clause classification (app/clauses/...)      termination, confidentiality, etc.
    -> Risk flagging (app/risk/risk_flagger.py)      rule-based + LLM-based scoring
    -> API (app/main.py)                             /analyze endpoint ties it together
    -> Frontend (not scaffolded yet)                 renders highlighted contract
```

## Why these model choices for v1

- **NER**: spaCy's `en_core_web_sm` gives DATE/ORG/PERSON/GPE out of the box for
  free and fast. Good enough for a working demo. Swap in a legal-domain
  transformer (`nlpaueb/legal-bert-base-uncased` fine-tuned for token
  classification) once you have time to fine-tune on labeled contract data.
- **Clause classification**: zero-shot classification via
  `facebook/bart-large-mnli` needs zero training data -- you just give it a
  label list. This is what makes a working demo possible in 5 days. If you
  have time, fine-tune a smaller model (e.g. `distilbert-base-uncased`) on a
  labeled clause dataset (CUAD dataset is a good public source) for
  speed + accuracy gains.
- **Risk flagging**: rule-based heuristics catch obvious red flags for free
  and deterministically. The LLM layer (`risk_flagger.llm_based_flag`) is
  pluggable -- wire in whichever LLM API your team has access to.

## Upgrade path (if you have extra time)

1. Fine-tune clause classifier on the [CUAD dataset](https://www.atticusprojectai.org/cuad)
   (13,000+ labeled clauses across 41 clause types).
2. Replace spaCy NER with a fine-tuned legal NER model.
3. Add a vector store (FAISS) over clause embeddings for semantic search
   ("find all clauses similar to this one across our contract database").
4. Add async processing (Celery + Redis) for large documents so uploads
   don't block the API thread.
5. Build the React dashboard that highlights entities/clauses/risk flags
   directly on the rendered contract text.

## Data flow contract

All modules communicate through the Pydantic models in `app/models/schemas.py`
(`ExtractedEntity`, `ClauseSegment`, `RiskFlag`, `DocumentAnalysis`). Keep this
as the single source of truth for what a "result" looks like -- it's what
lets each team member build their module independently without breaking
someone else's code.
