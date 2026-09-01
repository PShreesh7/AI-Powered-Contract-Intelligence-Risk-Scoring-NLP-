import { useState } from 'react';
import { downloadPdfReport } from '../api/client.js';

export default function DashboardHeader({ filename, file, overallRisk, onNewAnalysis }) {
  const [downloading, setDownloading] = useState(false);
  const [dlError, setDlError] = useState(null);

  async function handleDownloadPdf() {
    if (!file) return;
    setDownloading(true);
    setDlError(null);
    try {
      await downloadPdfReport(file);
    } catch (err) {
      setDlError(err.message);
    } finally {
      setDownloading(false);
    }
  }

  const riskColor = overallRisk >= 70 ? 'var(--risk-high)'
                  : overallRisk >= 40 ? 'var(--risk-med)'
                  : 'var(--risk-low)';

  return (
    <header className="dash-header">
      {/* Brand */}
      <a href="#" className="dash-brand" onClick={e => { e.preventDefault(); onNewAnalysis(); }} aria-label="Go to LexAI home">
        <div className="dash-brand-icon">⚖️</div>
        <span className="dash-brand-name">Lex<em>AI</em></span>
      </a>

      <div className="dash-divider" aria-hidden="true" />

      {/* File name */}
      <div className="dash-filename">
        <span className="filename-icon">📄</span>
        <span className="filename-text" title={filename}>{filename}</span>
      </div>

      {/* Risk pill */}
      <div
        style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '12px',
          color: riskColor,
          background: `${riskColor}18`,
          border: `1px solid ${riskColor}44`,
          borderRadius: 'var(--radius-full)',
          padding: '4px 12px',
          flexShrink: 0,
          letterSpacing: '0.04em',
        }}
        aria-label={`Overall risk score: ${overallRisk}`}
      >
        Risk {overallRisk}/100
      </div>

      {/* Actions */}
      <div className="dash-actions">
        {dlError && (
          <span style={{ fontSize: '12px', color: 'var(--risk-high)' }} title={dlError}>
            ⚠ PDF failed
          </span>
        )}
        <button
          id="download-pdf-btn"
          className="btn btn-ghost"
          onClick={handleDownloadPdf}
          disabled={downloading || !file}
          aria-label="Download PDF risk report"
        >
          {downloading ? '⏳' : '⬇️'} {downloading ? 'Generating…' : 'PDF Report'}
        </button>
        <button
          id="new-analysis-btn"
          className="btn btn-primary"
          onClick={onNewAnalysis}
          aria-label="Start a new contract analysis"
        >
          + New Analysis
        </button>
      </div>
    </header>
  );
}
