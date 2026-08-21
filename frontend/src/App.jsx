import { useState } from 'react';
import Header from './components/Header.jsx';
import ContractViewer from './components/ContractViewer.jsx';
import ClauseList from './components/ClauseList.jsx';
import RiskGauge from './components/RiskGauge.jsx';
import { analyzeContract } from './api/client.js';

export default function App() {
  const [fileName, setFileName] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [selectedClauseId, setSelectedClauseId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeContract(file);
      setAnalysis(result);
      setSelectedClauseId(null);
    } catch (err) {
      setError(err.message || 'Something went wrong analyzing this contract.');
    } finally {
      setLoading(false);
    }
  }

  function handleSelectClause(id) {
    setSelectedClauseId(id);
    const el = document.getElementById(`clause-${id}`);
    el?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  return (
    <div className="app-shell">
      <Header fileName={fileName} onUpload={handleUpload} />

      <main className="app-main">
        <section className="viewer-pane">
          {loading && <div className="status-line">Analyzing contract…</div>}
          {error && <div className="status-line status-error">{error}</div>}
          {!loading && (
            <ContractViewer
              fullText={analysis?.fullText}
              clauses={analysis?.clauses || []}
              selectedClauseId={selectedClauseId}
              onSelectClause={handleSelectClause}
            />
          )}
        </section>

        <aside className="side-pane">
          {analysis ? (
            <>
              <RiskGauge score={analysis.overallRisk} />
              <h2 className="side-heading">Flagged clauses ({analysis.clauses.length})</h2>
              <ClauseList
                clauses={analysis.clauses}
                selectedClauseId={selectedClauseId}
                onSelectClause={handleSelectClause}
              />
            </>
          ) : (
            <div className="side-empty">
              <p>Risk score and flagged clauses will appear here once a contract is analyzed.</p>
            </div>
          )}
        </aside>
      </main>
    </div>
  );
}
