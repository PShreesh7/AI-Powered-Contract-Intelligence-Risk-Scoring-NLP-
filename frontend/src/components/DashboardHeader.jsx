import { useState } from 'react';
import { FileDown, PlusCircle, Scale, FileText, Loader2, Sparkles } from 'lucide-react';
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

  const riskColor =
    overallRisk >= 70
      ? '#ff4d4d'
      : overallRisk >= 40
      ? '#ffa600'
      : '#00e699';

  return (
    <header className="dash-header-3d">
      {/* Brand */}
      <a
        href="#"
        className="brand-link"
        onClick={(e) => {
          e.preventDefault();
          onNewAnalysis();
        }}
        aria-label="Go to Barr & Douds home"
      >
        <div className="barr-crest" style={{ width: 36, height: 36 }}>
          <Scale size={18} className="crest-icon" />
        </div>
        <div className="brand-text">
          <span className="brand-firm" style={{ fontSize: 16 }}>BARR &amp; DOUDS</span>
          <span className="brand-sub" style={{ fontSize: 8 }}>LEXAI CONTRACT INTELLIGENCE</span>
        </div>
      </a>

      <div className="header-v-divider" />

      {/* Contract File Tag */}
      <div className="contract-pill">
        <FileText size={15} className="file-icon" />
        <span className="filename" title={filename}>{filename}</span>
        <span className="file-status-dot" />
      </div>

      {/* Dynamic Risk Tag */}
      <div
        className="risk-hud-pill"
        style={{
          borderColor: `${riskColor}55`,
          background: `${riskColor}12`,
          color: riskColor,
          boxShadow: `0 0 16px ${riskColor}28`,
        }}
      >
        <span className="hud-label">RISK INDEX</span>
        <span className="hud-val">{overallRisk}</span>
        <span className="hud-max">/100</span>
      </div>

      {/* Action Buttons */}
      <div className="header-actions">
        {dlError && <span className="dl-error-toast">{dlError}</span>}

        <button
          className="btn-glass-report"
          onClick={handleDownloadPdf}
          disabled={downloading || !file}
          title="Export complete legal risk assessment as PDF"
        >
          {downloading ? (
            <Loader2 size={16} className="spin-icon" />
          ) : (
            <FileDown size={16} />
          )}
          <span>{downloading ? 'Generating PDF…' : 'PDF Report'}</span>
        </button>

        <button
          className="btn-cinematic-cta"
          onClick={onNewAnalysis}
          title="Upload and analyze another contract"
        >
          <PlusCircle size={16} />
          <span>New Analysis</span>
        </button>
      </div>
    </header>
  );
}
