// Thin wrapper around the backend (text_utils.py-powered) API.
//
// Expected backend contract — adjust to match your actual FastAPI/Flask routes:
//
//   POST /api/analyze
//     body: { text: string }  OR  multipart file upload
//     returns: {
//       overallRisk: number (0-100),
//       clauses: [
//         {
//           id: string,
//           label: string,          // e.g. "Limitation of Liability"
//           text: string,           // the clause text, as found in the doc
//           startOffset: number,    // char offset into the full contract text
//           endOffset: number,
//           risk: "high" | "medium" | "low",
//           riskScore: number,      // 0-100
//           rationale: string       // why this clause was flagged
//         }
//       ],
//       fullText: string
//     }
//
// Until the backend is wired up, `analyzeContract` falls back to mock data
// so the frontend can be built and demoed independently.

const USE_MOCK = true; // flip to false once /api/analyze is live

export async function analyzeContract(fileOrText) {
  if (USE_MOCK) {
    const { mockAnalysis } = await import('./mockData.js');
    return new Promise((resolve) => setTimeout(() => resolve(mockAnalysis), 500));
  }

  const formData = new FormData();
  if (typeof fileOrText === 'string') {
    formData.append('text', fileOrText);
  } else {
    formData.append('file', fileOrText);
  }

  const res = await fetch('/api/analyze', {
    method: 'POST',
    body: formData
  });

  if (!res.ok) {
    throw new Error(`Analysis failed: ${res.status} ${res.statusText}`);
  }

  return res.json();
}
