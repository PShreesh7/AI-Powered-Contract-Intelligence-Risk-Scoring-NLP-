# Team guide: who does what

This explains, in plain language, what each person builds, why it matters, and
exactly what commands to run. Read your section, then follow it day by day.

Everyone starts with the same setup:

```bash
git clone <your-repo-url>
cd legal-nlp-platform
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Two sample contracts are already in `data/sample_contracts/` — use these to
test your work. You don't need to find your own test files.

---

## Person A — Ingestion & preprocessing

**In plain words:** Your job is to open the contract file (PDF or Word) and
turn it into plain text the rest of the pipeline can read. Then split that
text into individual clauses (paragraph 1, paragraph 2, etc.) so each part
can be analyzed separately.

**Your files:** `app/ingestion/parser.py`, `app/utils/text_utils.py`

**What to do, Day 1:**
1. Open `app/ingestion/parser.py` — it already extracts text from PDF and
   DOCX files. Test it:
   ```bash
   python app/ingestion/parser.py data/sample_contracts/Sample_Master_Service_Agreement.pdf
   ```
   You should see the contract text printed.
2. Try it on the DOCX file too. If either breaks on a weird contract format
   later, this is the file to fix.
3. Look at `app/utils/text_utils.py` — this cleans messy text and splits it
   into clauses. Test it:
   ```bash
   python -c "
   from app.ingestion.parser import extract_text
   from app.utils.text_utils import clean_text, split_into_clauses
   t = clean_text(extract_text('data/sample_contracts/Sample_Master_Service_Agreement.pdf'))
   clauses = split_into_clauses(t)
   print(f'{len(clauses)} clauses found')
   for c in clauses: print('-', c[:60])
   "
   ```
   You should see 11 clauses listed.
4. Commit your work: `git add app/ingestion app/utils && git commit -m "feat(ingestion): verified PDF/DOCX extraction and clause splitting"`

**If something breaks:** the extraction might miss text from scanned/image
PDFs (this only reads text-based PDFs, not photos of paper). That's a known
limitation — mention it in your README notes, don't try to fix OCR unless
you have spare time on day 5.

---

## Person B — NER (finding names, dates, places)

**In plain words:** Your job is to scan the contract text and pull out
important facts automatically — who the parties are, what dates matter, and
which country/state's laws apply. Think of it like highlighting a paper
contract with a marker for every important fact.

**Your file:** `app/ner/entity_extractor.py`

**What to do, Day 2:**
1. Test the existing extractor:
   ```bash
   python app/ner/entity_extractor.py
   ```
   This runs on a short built-in example. You should see entities printed
   with labels like DATE, PARTY, JURISDICTION.
2. Now test it on a real contract:
   ```bash
   python -c "
   from app.ingestion.parser import extract_text
   from app.utils.text_utils import clean_text
   from app.ner.entity_extractor import EntityExtractor
   t = clean_text(extract_text('data/sample_contracts/Sample_Master_Service_Agreement.pdf'))
   e = EntityExtractor()
   for ent in e.extract(t):
       print(ent.label, '->', ent.text)
   "
   ```
3. Check the output. Did it catch "Orion Technologies Private Limited" as a
   PARTY? Did it catch "March 14, 2024" as a DATE? If entities are missing or
   wrong, that's your job to tune — look at `LABEL_MAP` and the
   `JURISDICTION_PATTERN` regex near the top of the file.
4. Write 2-3 small tests in a new file `tests/test_ner.py` checking that
   known entities get found.
5. Commit: `git add app/ner tests/test_ner.py && git commit -m "feat(ner): tuned entity extraction, added tests"`

**Why this matters:** without this, nobody knows who signed the contract or
when it expires without reading the whole thing manually.

---

## Person C — Clause classification (labeling each paragraph)

**In plain words:** Your job is to label every paragraph with what kind of
clause it is — "this one is about termination," "this one is about
confidentiality," and so on. This is what lets the final dashboard show
"here's the termination clause" instead of a wall of unlabeled text.

**Your file:** `app/clauses/clause_classifier.py`

**What to do, Day 3:**
1. This uses an AI model that can label text without needing training data
   first (called "zero-shot classification") — it's slower on first run
   because it downloads the model (~1.6GB), so run this early in the day:
   ```bash
   python app/clauses/clause_classifier.py
   ```
2. Test on a real contract:
   ```bash
   python -c "
   from app.ingestion.parser import extract_text
   from app.utils.text_utils import clean_text, split_into_clauses
   from app.clauses.clause_classifier import ClauseClassifier
   t = clean_text(extract_text('data/sample_contracts/Sample_Master_Service_Agreement.pdf'))
   clauses = split_into_clauses(t)
   offsets = [(0, len(c)) for c in clauses]
   clf = ClauseClassifier()
   for result in clf.classify(clauses, offsets):
       print(result.clause_type, '(', result.confidence, ') ->', result.text[:50])
   "
   ```
3. Check: did it correctly guess "termination" for the termination clause?
   If labels look wrong, look at the `CLAUSE_LABELS` list near the top —
   you can add/remove label options to improve accuracy.
4. Write tests in `tests/test_clauses.py` checking a known clause gets the
   right label.
5. Commit: `git add app/clauses tests/test_clauses.py && git commit -m "feat(clauses): tuned clause classification, added tests"`

**Why this matters:** this is the "brain" that organizes the contract into
sections a lawyer actually cares about, instead of raw text.

---

## Person D — Risk flagging (finding dangerous language)

**In plain words:** Your job is to look at each labeled clause and decide:
is this normal, or is it unusually risky? For example, "company can cancel
for any reason, no notice needed" is a red flag. There are two layers:
simple rule-based checks (fast, free, already built) and AI-based checks
(smarter, needs an API key).

**Your file:** `app/risk/risk_flagger.py`

**What to do, Day 3-4:**
1. The rule-based layer is already built and tested — it catches phrases
   like "sole discretion," "unlimited liability," "perpetual." Test it:
   ```bash
   python -c "
   from app.models.schemas import ClauseSegment
   from app.risk.risk_flagger import rule_based_flags
   seg = ClauseSegment(clause_id='1', text='Company may terminate at its sole discretion.', clause_type='termination', confidence=1.0, start_char=0, end_char=10)
   print(rule_based_flags(seg))
   "
   ```
2. Look at `RISK_RULES` near the top of the file — add 2-3 more rules for
   patterns you think are risky (e.g. very short notice periods, one-sided
   auto-renewal clauses).
3. **Day 4:** wire up the AI layer. You need an API key from whichever LLM
   your team has access to (Anthropic, OpenAI, etc.). Write a small function
   that sends a prompt to that API and returns the response, then pass it
   into `flag_risks(clauses, call_llm_fn=your_function)`. There's a template
   prompt already written for you (`RISK_PROMPT_TEMPLATE`) — you just need
   to plug in the actual API call.
4. **Important:** put your API key in a `.env` file, never commit it directly
   in code. Add `.env` to `.gitignore` if it isn't already there.
5. Commit: `git add app/risk && git commit -m "feat(risk): added rules and LLM-based risk scoring"`

**Why this matters:** this is the actual "value" of the whole project — it's
the part that saves a lawyer from having to read every clause manually to
catch something dangerous.

---

## Person E — API, integration, testing, docs

**In plain words:** Your job is to connect everyone else's work into one
working system, plus make sure it actually runs from a clean download and
write the instructions so anyone (including graders) can use it.

**Your files:** `app/main.py`, `tests/`, `README.md`

**What to do, Day 1-3:** review everyone's schemas in `app/models/schemas.py`
early — this is the shared contract format everyone builds against. Flag any
changes needed before others build on it. Help unblock whoever's stuck.

**Day 4-5, the main work:**
1. Start the API:
   ```bash
   uvicorn app.main:app --reload
   ```
2. Test the full pipeline with a real upload:
   ```bash
   curl -X POST "http://127.0.0.1:8000/analyze" \
     -F "file=@data/sample_contracts/Sample_Master_Service_Agreement.pdf"
   ```
   You should get back JSON with entities, clauses, and risk flags all
   together. If something breaks here, it's usually because two people's
   modules don't agree on the data format — check `app/models/schemas.py`.
3. Run all tests: `pytest` — fix any failures.
4. Update `README.md` with final setup steps and a sample request/response.
5. Do a final clean-clone test: clone the repo fresh into a new folder,
   follow your own README from scratch, make sure it actually works.
6. Tag the release: `git tag v0.1.0 && git push --tags`

**Why this matters:** without this, everyone's individual pieces are just
separate files that don't talk to each other. You're the glue.

---

## Quick reference: daily commit checklist (everyone)

- Pull latest changes before starting: `git pull`
- Work on your own branch: `git checkout -b feature/your-module`
- Commit small, often — 2-4 commits per day, not one giant commit
- Push and open a pull request into `main` at the end of each day
- Use clear commit messages: `feat(ner): add jurisdiction detection`, not
  `updates` or `fix stuff`

If your commit history shows 5 days of real, incremental work from every
person, that's exactly what this plan is designed to produce.
