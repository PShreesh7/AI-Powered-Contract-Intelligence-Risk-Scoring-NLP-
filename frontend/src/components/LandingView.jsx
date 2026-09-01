import { useState, useRef } from 'react';

const FEATURES = [
  {
    icon: '🔍',
    title: 'Named Entity Extraction',
    desc: 'Automatically extracts parties, dates, jurisdictions, and monetary values using spaCy NER.',
  },
  {
    icon: '⚠️',
    title: 'Risk Clause Detection',
    desc: 'Identifies indemnification, auto-renewal, liability caps, and 41+ legal clause types.',
  },
  {
    icon: '🤖',
    title: 'AI Q&A',
    desc: 'Ask plain-language questions about any contract — powered by Gemini LLM.',
  },
];

export default function LandingView({ onUpload, error }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef(null);

  function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (file) onUpload(file);
  }

  function handleDrop(e) {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) onUpload(file);
  }

  function handleDragOver(e) {
    e.preventDefault();
    setIsDragOver(true);
  }

  function handleDragLeave() {
    setIsDragOver(false);
  }

  return (
    <div className="landing">
      {/* Animated background */}
      <div className="landing-bg">
        <div className="landing-grid" />
        <div className="landing-orb landing-orb-1" />
        <div className="landing-orb landing-orb-2" />
        <div className="landing-orb landing-orb-3" />
      </div>

      {/* Nav */}
      <nav className="landing-nav">
        <div className="nav-brand">
          <div className="nav-brand-icon">⚖️</div>
          <span className="nav-brand-name">Lex<em>AI</em></span>
        </div>
        <span className="nav-badge">NLP · CUAD · v1.0</span>
      </nav>

      <div className="landing-content" style={{ paddingTop: '80px' }}>
        {/* Hero */}
        <div className="landing-hero">
          <div className="hero-eyebrow">
            <span className="hero-eyebrow-dot" />
            AI-Powered Contract Intelligence
          </div>

          <h1 className="hero-title">
            Find hidden risks in<br />
            <span className="gradient-text">legal contracts</span><br />
            in seconds
          </h1>

          <p className="hero-subtitle">
            Upload any PDF or Word contract. Our NLP pipeline extracts key entities,
            classifies 41+ clause types, and flags high-risk language — instantly.
          </p>

          {/* Upload Zone */}
          <div
            className={`upload-zone ${isDragOver ? 'drag-over' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => inputRef.current?.click()}
            role="button"
            tabIndex={0}
            aria-label="Upload contract file"
            onKeyDown={e => e.key === 'Enter' && inputRef.current?.click()}
          >
            <input
              id="contract-upload"
              ref={inputRef}
              type="file"
              accept=".pdf,.docx,.txt"
              className="upload-input"
              onChange={handleFileChange}
            />
            <div className="upload-icon">📄</div>
            <div className="upload-title">
              {isDragOver ? 'Drop to analyze' : 'Drop your contract here'}
            </div>
            <div className="upload-subtitle">
              or click to browse your files
            </div>
            <div className="upload-formats">
              <span className="format-chip">PDF</span>
              <span className="format-chip">DOCX</span>
              <span className="format-chip">TXT</span>
            </div>
          </div>

          {error && (
            <div className="error-banner" style={{ marginTop: '16px', maxWidth: '540px' }}>
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Features */}
        <div className="features-grid">
          {FEATURES.map(f => (
            <div key={f.title} className="feature-card">
              <div className="feature-icon">{f.icon}</div>
              <div className="feature-title">{f.title}</div>
              <div className="feature-desc">{f.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
