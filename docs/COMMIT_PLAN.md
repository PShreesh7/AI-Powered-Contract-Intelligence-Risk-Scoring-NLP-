# 5-day build + commit plan

Team of 5. The goal is a **real commit every day from every person** --
graders/mentors usually check commit history, not just the final result, so
don't dump everything on day 5.

Roles:
- **A -- Ingestion & preprocessing** (`app/ingestion/`, `app/utils/`)
- **B -- NER** (`app/ner/`)
- **C -- Clause classification** (`app/clauses/`)
- **D -- Risk flagging + LLM integration** (`app/risk/`)
- **E -- API, integration, testing, docs** (`app/main.py`, `tests/`, README)

E has the lightest Day 1-3 load and the heaviest Day 4-5 load (wiring
everyone's modules together), so E can also help pair with whoever's blocked
on a given day.

---

## Day 1 -- Setup + ingestion

- Everyone: clone repo, set up virtualenv, `pip install -r requirements.txt`,
  run `python -m spacy download en_core_web_sm`.
- **A**: finalize `app/ingestion/parser.py` (PDF/DOCX extraction), test against
  the two sample contracts already in `data/sample_contracts/`
  (`Sample_Master_Service_Agreement.pdf`, `Sample_Consulting_NDA_Agreement.docx`).
  Both contain numbered clauses across ~10 clause types and a few deliberately
  planted risky phrases ("sole discretion", "unlimited liability", "in
  perpetuity") so the risk flagger has something real to catch.
- **A**: finalize `app/utils/text_utils.py` (cleaning + clause splitting).
- **Everyone else**: read `docs/ARCHITECTURE.md`, review schemas in
  `app/models/schemas.py`, flag anything you want changed before building
  on top of it.

Commit message examples:
- `feat(ingestion): add PDF/DOCX text extraction`
- `feat(utils): add text cleaning and clause segmentation`
- `docs: add architecture overview`

## Day 2 -- NER module

- **B**: build out `app/ner/entity_extractor.py`, test against sample
  contracts from Day 1, tune the jurisdiction regex against real clauses.
- **B**: add `tests/test_ner.py` with a few known-entity assertions.
- **C**: start scaffolding `app/clauses/clause_classifier.py` in parallel
  (zero-shot classifier doesn't depend on NER being done).

Commit message examples:
- `feat(ner): implement entity extraction with spaCy + regex jurisdiction detection`
- `test(ner): add entity extraction unit tests`

## Day 3 -- Clause classification

- **C**: finish `app/clauses/clause_classifier.py`, run it against sample
  contracts, sanity-check label quality, tune `CLAUSE_LABELS` list if some
  clause types are missing or mislabeled.
- **C**: add `tests/test_clauses.py`.
- **D**: start `app/risk/risk_flagger.py` rule-based layer -- doesn't need
  clause classifier finished, can test rules against dummy `ClauseSegment` objects.

Commit message examples:
- `feat(clauses): implement zero-shot clause classification`
- `test(clauses): add classifier unit tests`
- `feat(risk): add rule-based risk heuristics`

## Day 4 -- Risk flagging + integration prep

- **D**: finish rule-based risk layer, wire up the LLM-based layer
  (`llm_based_flag`) using whichever API key the team has (Anthropic API,
  OpenAI, etc.) -- keep the API key in a `.env` file, never commit it.
- **E**: start wiring `app/main.py` end-to-end, run the full pipeline
  manually on a sample contract, fix integration bugs (offset mismatches,
  schema mismatches between modules).

Commit message examples:
- `feat(risk): add LLM-based risk scoring`
- `feat(api): wire up /analyze endpoint end-to-end`
- `fix(api): correct clause offset tracking`

## Day 5 -- Polish, tests, docs, demo prep

- **E**: finish `/analyze` endpoint, add `/health`, write remaining tests in
  `tests/`, run `pytest` and fix failures.
- **Everyone**: update `README.md` with setup instructions and a demo
  screenshot/GIF if you have a frontend, or a sample `curl` request +
  response if you don't.
- **Everyone**: final review pass -- pull latest, resolve conflicts, make
  sure `pip install -r requirements.txt && uvicorn app.main:app --reload`
  works from a clean clone.
- Tag a release: `git tag v0.1.0 && git push --tags`.

Commit message examples:
- `test: add end-to-end API tests`
- `docs: update README with setup and demo instructions`
- `chore: final cleanup before submission`

---

## Git workflow tips for the team

- One branch per person (`feature/ner`, `feature/clauses`, etc.), PR into `main`
  daily -- this is what actually produces 5 days of visible commits instead
  of one big squash at the end.
- Small, frequent commits beat one giant commit. Aim for 2-4 commits/day/person.
- Put your name or initials in commit messages if your grading criteria
  wants individual contribution visible: `feat(ner): add jurisdiction regex [B]`.
- If two people touch `app/main.py`, coordinate in advance -- integration
  conflicts on the wiring file are the most common source of merge pain.
