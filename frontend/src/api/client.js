/**
 * LexAI — API Client
 * Connects the React frontend to the FastAPI backend.
 *
 * Backend routes:
 *   POST /analyze              → returns AnalyzeResponse JSON
 *   POST /analyze/pdf-report   → returns downloadable PDF bytes
 *   POST /ask                  → returns { status, answer }
 *
 * The backend schema is normalized here into the frontend shape
 * so components stay decoupled from implementation details.
 */

// ─── Toggle for local dev without a running backend ────────────────────────
const USE_MOCK = false;   // flip to true to use mockData.js

// ─── Response normalizer ───────────────────────────────────────────────────
// Backend → Frontend shape mapping.
// Backend: { status, analysis: { document_id, filename, raw_text_length,
//              entities, clauses, risk_flags } }
// Frontend: { overallRisk, clauses, entities, metadata, fullText }
function normalizeAnalysis(backendResponse) {
  const { analysis } = backendResponse;
  if (!analysis) throw new Error('Empty analysis response from server.');

  const { clauses: rawClauses, risk_flags, entities, filename, raw_text_length, document_id } = analysis;

  // Build a lookup map: clause_id → risk_flag
  const riskMap = {};
  for (const flag of risk_flags ?? []) {
    riskMap[flag.clause_id] = flag;
  }

  // Merge clause segments with their risk flags into frontend clause objects
  const clauses = (rawClauses ?? []).map((c, i) => {
    const flag = riskMap[c.clause_id] ?? {};
    const riskLevel = flag.risk_level ?? 'low';
    const riskScore = riskLevel === 'high' ? 80 + Math.round(c.confidence * 15)
                    : riskLevel === 'medium' ? 45 + Math.round(c.confidence * 20)
                    : 10 + Math.round(c.confidence * 20);
    return {
      id:         c.clause_id,
      label:      formatClauseLabel(c.clause_type),
      clauseType: c.clause_type,
      text:       c.text,
      startOffset: c.start_char,
      endOffset:   c.end_char,
      risk:        riskLevel,
      riskScore:   Math.min(riskScore, 99),
      confidence:  c.confidence,
      rationale:   flag.reason ?? 'Clause identified by NLP model.',
      suggestion:  flag.suggestion ?? null,
    };
  });

  // Compute overall risk as weighted average of clause risk scores
  const overallRisk = clauses.length
    ? Math.round(clauses.reduce((s, c) => s + c.riskScore, 0) / clauses.length)
    : 0;

  // Reconstruct approximate full text from clause spans (or join)
  const fullText = clauses.map(c => c.text).join('\n\n');

  return {
    documentId:    document_id,
    filename,
    rawTextLength: raw_text_length,
    overallRisk,
    clauses,
    entities:      entities ?? [],
    fullText,
  };
}

function formatClauseLabel(clauseType) {
  if (!clauseType) return 'Clause';
  return clauseType
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase());
}

// ─── Public API ────────────────────────────────────────────────────────────

/**
 * Upload a contract file and receive normalized analysis results.
 * @param {File} file - PDF, DOCX, or TXT file
 * @returns {Promise<object>} normalized analysis object
 */
export async function analyzeContract(file) {
  if (USE_MOCK) {
    const { mockAnalysis } = await import('./mockData.js');
    return new Promise(resolve => setTimeout(() => resolve(mockAnalysis), 1800));
  }

  const formData = new FormData();
  formData.append('file', file);

  let res;
  try {
    res = await fetch('/analyze', {
      method: 'POST',
      body: formData,
    });
  } catch (networkErr) {
    throw new Error(
      'Cannot reach the backend server. Please start it with:\n' +
      '  uvicorn app.main:app --reload\n' +
      'Then try again. (Backend must be running on port 8000)'
    );
  }

  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `Analysis failed: ${res.status} ${res.statusText}`);
  }

  const json = await res.json();
  return normalizeAnalysis(json);
}

/**
 * Download the PDF risk report for the given contract file.
 * Triggers a browser download automatically.
 * @param {File} file
 * @returns {Promise<void>}
 */
export async function downloadPdfReport(file) {
  const formData = new FormData();
  formData.append('file', file);

  let res;
  try {
    res = await fetch('/analyze/pdf-report', {
      method: 'POST',
      body: formData,
    });
  } catch (networkErr) {
    throw new Error('Backend server is not reachable. Please ensure uvicorn is running on port 8000.');
  }

  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `PDF report failed: ${res.status}`);
  }

  const blob = await res.blob();
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = `${file.name.replace(/\.[^.]+$/, '')}_risk_report.pdf`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Ask a plain-language question about a contract's clauses.
 * @param {string[]} clauseTexts - array of clause text strings
 * @param {string} question
 * @returns {Promise<string>} AI-generated answer
 */
export async function askContractQuestion(clauseTexts, question) {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 1200));
    return `Based on the contract clauses provided, ${question.toLowerCase().includes('terminat') 
      ? 'the agreement can be terminated by either party with 30 days written notice.'
      : question.toLowerCase().includes('liab')
      ? 'liability is capped and consequential damages are excluded by both parties.'
      : 'I found relevant provisions in the contract that address your question. Please review the highlighted clauses for detailed information.'}`;
  }

  let res;
  try {
    res = await fetch('/ask', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, clause_texts: clauseTexts }),
    });
  } catch (networkErr) {
    throw new Error('Backend server is not reachable. Please ensure uvicorn is running on port 8000.');
  }

  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `Q&A request failed: ${res.status}`);
  }

  const json = await res.json();
  return json.answer ?? 'No answer available.';
}
