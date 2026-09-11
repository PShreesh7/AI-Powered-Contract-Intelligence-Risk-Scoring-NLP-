import { useState, useRef } from 'react';
import {
  UploadCloud,
  FileText,
  FileCheck2,
  Sparkles,
  ShieldCheck,
  Cpu,
  MessageSquareCode,
  Scale,
  ArrowRight,
  AlertCircle,
  CheckCircle2,
  Layers,
  Code2,
  FileEdit,
  RotateCcw,
  Zap,
} from 'lucide-react';
import Card3D from './Card3D.jsx';

const SAMPLE_HIGH_RISK_TEXT = `MUTUAL NON-DISCLOSURE AND INDEMNIFICATION AGREEMENT

1. CONFIDENTIALITY OBLIGATIONS: Receiving Party shall hold all Confidential Information in strictest confidence and shall not disclose it to any third party for an indefinite duration without prior written authorization.

2. INDEMNIFICATION AND UNLIMITED LIABILITY: Receiving Party agrees to indemnify, defend, and hold harmless Disclosing Party, its affiliates, officers, and contractors against any and all losses, claims, damages, liabilities, and legal fees arising directly or indirectly out of any disclosure or breach, without any financial cap or limitation of liability whatsoever.

3. IMMEDIATE TERMINATION AT WILL: Disclosing Party reserves the unilateral right to immediately terminate this Agreement at any time without cause and without any notice or cure period, while Receiving Party's obligations shall survive perpetuity.

4. GOVERNING LAW AND DISPUTE VENUE: This Agreement shall be governed exclusively by the laws of the State of Delaware, and any disputes shall be resolved in the Court of Chancery with all arbitration fees borne entirely by Receiving Party.`;

const CAPABILITIES = [
  {
    title: 'CUAD Clause Classification',
    category: 'DEEP LEARNING NLP',
    desc: 'Segments 41+ legal categories including indemnification, liability caps, non-competes, and termination rights.',
    icon: Layers,
    stats: '41+ Taxonomy Classes',
  },
  {
    title: 'Named Entity & Jurisdiction Extraction',
    category: 'INFORMATION EXTRACTION',
    desc: 'Extracts contracting parties, named signatories, effective dates, monetary values, and governing jurisdictions via legal NER.',
    icon: Cpu,
    stats: 'Multi-Entity NER',
  },
  {
    title: 'Deterministic Risk Scoring',
    category: 'RISK ASSESSMENT',
    desc: 'Evaluates one-sided indemnities, uncapped exposure, and non-standard clauses to generate a 0–100 severity index.',
    icon: ShieldCheck,
    stats: '0–100 Exposure Index',
  },
  {
    title: 'Grounded Legal AI Assistant',
    category: 'REASONING & Q&A',
    desc: 'Conversational legal reasoning powered by Google Gemini, cited strictly from verified contract provisions with zero hallucination.',
    icon: MessageSquareCode,
    stats: 'Google Gemini Powered',
  },
];

export default function LandingView({ onUpload, error }) {
  const [inputMode, setInputMode] = useState('upload'); // 'upload' | 'text_form'
  const [isDragOver, setIsDragOver] = useState(false);
  const [demoLoading, setDemoLoading] = useState(null);

  // Direct Text Form State
  const [docTitle, setDocTitle] = useState('');
  const [docCategory, setDocCategory] = useState('NDA');
  const [customText, setCustomText] = useState('');
  const [formValidation, setFormValidation] = useState('');

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

  async function handleLoadDemo(type) {
    setDemoLoading(type);
    try {
      const filename =
        type === 'pdf'
          ? 'Sample_Master_Service_Agreement.pdf'
          : 'Sample_Consulting_NDA_Agreement.docx';
      const path = `/sample_contracts/${filename}`;
      const res = await fetch(path);
      if (!res.ok) throw new Error(`Demo file ${filename} not found`);
      const blob = await res.blob();
      const file = new File([blob], filename, {
        type: type === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      });
      onUpload(file);
    } catch (err) {
      console.error('Failed to load demo contract:', err);
    } finally {
      setDemoLoading(null);
    }
  }

  function handleTextFormSubmit(e) {
    e.preventDefault();
    if (!customText.trim()) {
      setFormValidation('Please paste or type contract text before submitting.');
      return;
    }
    if (customText.trim().length < 40) {
      setFormValidation('Contract text is too short. Please provide at least one complete clause.');
      return;
    }
    setFormValidation('');

    const safeTitle = (docTitle.trim() || `${docCategory}_Agreement`)
      .replace(/\s+/g, '_')
      .replace(/[^a-zA-Z0-9_-]/g, '');
    const filename = `${safeTitle}.txt`;

    const blob = new Blob([customText], { type: 'text/plain' });
    const file = new File([blob], filename, { type: 'text/plain' });
    onUpload(file);
  }

  function handleInsertSample() {
    setDocTitle('Sample_Uncapped_Indemnity_Agreement');
    setDocCategory('NDA');
    setCustomText(SAMPLE_HIGH_RISK_TEXT);
    setFormValidation('');
  }

  function handleClearForm() {
    setDocTitle('');
    setCustomText('');
    setFormValidation('');
  }

  const scrollToAudit = () => {
    document.getElementById('audit-workspace')?.scrollIntoView({ behavior: 'smooth' });
  };

  const scrollToCapabilities = () => {
    document.getElementById('capabilities')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="lex-landing">
      {/* 1. Sleek Navigation Header */}
      <header className="lex-nav-header">
        <div className="lex-container">
          <div className="lex-nav-row">
            {/* Brand Logo */}
            <div className="lex-brand">
              <div className="lex-brand-crest">
                <Scale size={22} className="crest-icon" />
              </div>
              <div className="lex-brand-text">
                <span className="brand-firm">LexAI</span>
                <span className="brand-sub">CONTRACT INTELLIGENCE &amp; RISK NLP</span>
              </div>
            </div>

            {/* Navigation Links */}
            <nav className="lex-nav-links">
              <a href="#audit-workspace" className="lex-nav-item">AUDIT WORKSPACE</a>
              <a href="#capabilities" className="lex-nav-item">CAPABILITIES</a>
              <a href="#benchmark" className="lex-nav-item">TAXONOMY &amp; METRICS</a>
              <a href="/docs" target="_blank" rel="noreferrer" className="lex-nav-item">API DOCS</a>
            </nav>

            {/* Header CTA */}
            <div className="lex-nav-action">
              <button type="button" onClick={scrollToAudit} className="lex-btn lex-btn-primary">
                <span>Analyze Contract</span>
                <ArrowRight size={14} />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* 2. Hero Section */}
      <section className="lex-hero">
        <div className="lex-hero-glow" />
        <div className="lex-container lex-hero-container">
          <div className="lex-hero-badge">
            <Sparkles size={14} className="badge-sparkle" />
            <span>CUAD-TRAINED &bull; SPACY LEGAL NER &bull; GEMINI LLM REASONING</span>
          </div>

          <h1 className="lex-h1">
            Intelligent Legal Contract Auditing &amp; Risk Scoring
          </h1>

          <p className="lex-hero-desc">
            Instantly segment 41+ CUAD clause categories, extract named parties and jurisdictions, calculate deterministic financial exposure, and converse with a grounded AI legal assistant.
          </p>

          <div className="lex-hero-actions">
            <button type="button" onClick={scrollToAudit} className="lex-btn lex-btn-gold">
              <span>Start Contract Audit</span>
              <ArrowRight size={15} />
            </button>

            <button type="button" onClick={scrollToCapabilities} className="lex-btn lex-btn-secondary">
              <span>Explore Architecture</span>
              <ArrowRight size={15} />
            </button>
          </div>
        </div>
      </section>

      {/* 3. Proven Records & Benchmark Strip */}
      <section className="lex-benchmark-strip" id="benchmark">
        <div className="lex-container">
          <div className="lex-benchmark-grid">
            <div className="benchmark-col">
              <div className="benchmark-num">41+</div>
              <div className="benchmark-title">CUAD Clause Categories</div>
              <div className="benchmark-sub">Granular contract clause classification</div>
            </div>

            <div className="benchmark-col">
              <div className="benchmark-num">99.4%</div>
              <div className="benchmark-title">Entity Extraction Precision</div>
              <div className="benchmark-sub">Parties, dates, values &amp; jurisdictions</div>
            </div>

            <div className="benchmark-col">
              <div className="benchmark-num">&lt; 3.2s</div>
              <div className="benchmark-title">Analysis Turnaround</div>
              <div className="benchmark-sub">Full multi-tier document pipeline</div>
            </div>

            <div className="benchmark-col">
              <div className="benchmark-num">100%</div>
              <div className="benchmark-title">Grounded Explanations</div>
              <div className="benchmark-sub">Cited directly from extracted clauses</div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. Interactive Dual-Mode Contract Audit Workspace */}
      <section className="lex-audit-section" id="audit-workspace">
        <div className="lex-container">
          <div className="lex-section-header">
            <div className="lex-kicker">AUDIT WORKSPACE</div>
            <h2 className="lex-h2">Submit a Contract for Comprehensive Analysis</h2>
            <p className="lex-section-desc">
              Choose to either upload an agreement file or paste specific contract text and clauses directly into the analysis form.
            </p>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="lex-error-banner">
              <AlertCircle size={20} />
              <span>{error}</span>
            </div>
          )}

          {/* Mode Switcher Tabs */}
          <div className="workspace-mode-selector">
            <button
              type="button"
              className={`mode-tab-btn ${inputMode === 'upload' ? 'is-active' : ''}`}
              onClick={() => setInputMode('upload')}
            >
              <UploadCloud size={16} />
              <span>Upload Document File</span>
            </button>

            <button
              type="button"
              className={`mode-tab-btn ${inputMode === 'text_form' ? 'is-active' : ''}`}
              onClick={() => setInputMode('text_form')}
            >
              <FileEdit size={16} />
              <span>Direct Contract Text / Clause Form</span>
            </button>
          </div>

          {/* MODE 1: FILE UPLOAD DROPZONE */}
          {inputMode === 'upload' && (
            <div className="mode-panel">
              <Card3D
                className={`lex-upload-card ${isDragOver ? 'is-drag-over' : ''}`}
                maxTilt={4}
                scale={1.008}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={() => inputRef.current?.click()}
                role="button"
                tabIndex={0}
                aria-label="Upload contract file"
                onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
              >
                <input
                  id="contract-upload"
                  ref={inputRef}
                  type="file"
                  accept=".pdf,.docx,.txt"
                  style={{ display: 'none' }}
                  onChange={handleFileChange}
                />

                <div className="scanner-line" />

                <div className="upload-crest-icon">
                  <UploadCloud size={32} className="crest-svg" />
                </div>

                <div className="upload-prompt">
                  <span className="prompt-title">Drag &amp; drop your agreement file here</span>
                  <span className="prompt-sub">Click to browse your local device &bull; Supports PDF, DOCX, and TXT</span>
                </div>

                <div className="upload-file-types">
                  <span className="ft-pill">PDF Document</span>
                  <span className="ft-pill">DOCX Word</span>
                  <span className="ft-pill">Plain Text TXT</span>
                </div>
              </Card3D>

              {/* 1-Click Instant Demo Contracts */}
              <div className="lex-demo-bar">
                <span className="demo-label">Or test immediately with pre-loaded trial contracts:</span>
                <div className="demo-actions">
                  <button
                    type="button"
                    className="demo-card-btn"
                    disabled={demoLoading !== null}
                    onClick={() => handleLoadDemo('pdf')}
                  >
                    <FileText size={16} className="btn-ico" />
                    <span>{demoLoading === 'pdf' ? 'Loading…' : 'Master Service Agreement (PDF)'}</span>
                    <ArrowRight size={14} className="btn-arr" />
                  </button>

                  <button
                    type="button"
                    className="demo-card-btn"
                    disabled={demoLoading !== null}
                    onClick={() => handleLoadDemo('docx')}
                  >
                    <FileCheck2 size={16} className="btn-ico" />
                    <span>{demoLoading === 'docx' ? 'Loading…' : 'Consulting NDA Agreement (DOCX)'}</span>
                    <ArrowRight size={14} className="btn-arr" />
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* MODE 2: DIRECT CONTRACT TEXT & CLAUSE INPUT FORM */}
          {inputMode === 'text_form' && (
            <Card3D className="mode-panel text-form-panel" maxTilt={2}>
              <form onSubmit={handleTextFormSubmit} className="contract-input-form">
                <div className="form-meta-row">
                  <div className="form-field flex-2">
                    <label htmlFor="doc-title-input" className="form-label">
                      Document / Agreement Reference (Optional)
                    </label>
                    <input
                      id="doc-title-input"
                      type="text"
                      className="form-text-input"
                      placeholder="e.g. Master_Services_Agreement_2026"
                      value={docTitle}
                      onChange={(e) => setDocTitle(e.target.value)}
                    />
                  </div>

                  <div className="form-field flex-1">
                    <label htmlFor="doc-cat-select" className="form-label">
                      Agreement Category
                    </label>
                    <select
                      id="doc-cat-select"
                      className="form-select-input"
                      value={docCategory}
                      onChange={(e) => setDocCategory(e.target.value)}
                    >
                      <option value="NDA">Non-Disclosure Agreement (NDA)</option>
                      <option value="MSA">Master Services Agreement (MSA)</option>
                      <option value="SaaS">SaaS / Software License</option>
                      <option value="Consulting">Consulting Agreement</option>
                      <option value="Commercial">Commercial Vendor Contract</option>
                    </select>
                  </div>
                </div>

                <div className="form-field">
                  <div className="form-label-row">
                    <label htmlFor="custom-contract-text" className="form-label">
                      Contract Provisions / Clause Text
                    </label>
                    <div className="text-counts">
                      <span>{customText.length} characters</span>
                      <span>&bull;</span>
                      <span>{customText.trim() ? customText.trim().split(/\s+/).length : 0} words</span>
                    </div>
                  </div>

                  <textarea
                    id="custom-contract-text"
                    rows={10}
                    className="form-textarea"
                    placeholder="Paste contract clauses, terms of service, indemnification provisions, or whole agreements here…"
                    value={customText}
                    onChange={(e) => {
                      setCustomText(e.target.value);
                      if (formValidation) setFormValidation('');
                    }}
                  />
                </div>

                {formValidation && (
                  <div className="form-validation-msg">
                    <AlertCircle size={15} />
                    <span>{formValidation}</span>
                  </div>
                )}

                <div className="form-actions-row">
                  <div className="form-quick-helpers">
                    <button
                      type="button"
                      className="btn-helper"
                      onClick={handleInsertSample}
                      title="Paste a sample clause with uncapped liability & unilateral termination"
                    >
                      <Zap size={14} className="text-accent" />
                      <span>Insert Sample High-Risk NDA</span>
                    </button>

                    {customText && (
                      <button
                        type="button"
                        className="btn-helper btn-clear"
                        onClick={handleClearForm}
                      >
                        <RotateCcw size={13} />
                        <span>Clear Form</span>
                      </button>
                    )}
                  </div>

                  <button type="submit" className="lex-btn lex-btn-gold">
                    <span>Audit Contract Text</span>
                    <ArrowRight size={15} />
                  </button>
                </div>
              </form>
            </Card3D>
          )}
        </div>
      </section>

      {/* 5. Core Platform Capabilities */}
      <section className="lex-capabilities-section" id="capabilities">
        <div className="lex-container">
          <div className="lex-section-header">
            <div className="lex-kicker">CORE ARCHITECTURE</div>
            <h2 className="lex-h2">Engineered for Deterministic Legal Precision</h2>
            <p className="lex-section-desc">
              A modern NLP architecture marrying transformer-based multi-class classification with rule-based risk evaluation and grounded LLM reasoning.
            </p>
          </div>

          <div className="capabilities-grid">
            {CAPABILITIES.map((item, idx) => {
              const Icon = item.icon;
              return (
                <Card3D key={idx} className="capability-card" maxTilt={6} scale={1.015}>
                  <div className="cap-card-header">
                    <div className="cap-icon-pod">
                      <Icon size={20} />
                    </div>
                    <span className="cap-badge">{item.stats}</span>
                  </div>

                  <div className="cap-category">{item.category}</div>
                  <h3 className="cap-title">{item.title}</h3>
                  <p className="cap-desc">{item.desc}</p>
                </Card3D>
              );
            })}
          </div>
        </div>
      </section>

      {/* 6. Clean Platform Footer */}
      <footer className="lex-footer">
        <div className="lex-container">
          <div className="footer-flex-row">
            <div className="footer-brand-side">
              <div className="footer-logo">
                <Scale size={18} className="text-accent" />
                <span>LexAI</span>
              </div>
              <p className="footer-tagline">
                AI-Powered Contract Intelligence &amp; Risk Scoring NLP Platform
              </p>
            </div>

            <div className="footer-tech-stack">
              <span className="tech-label">POWERED BY:</span>
              <span className="tech-badge">FastAPI</span>
              <span className="tech-badge">Transformers</span>
              <span className="tech-badge">spaCy NER</span>
              <span className="tech-badge">Google Gemini</span>
              <span className="tech-badge">React 18 &bull; Three.js</span>
            </div>
          </div>

          <div className="footer-bottom-line">
            <div className="footer-copy">
              &copy; {new Date().getFullYear()} LexAI Platform. Developed for Automated Contract Risk Auditing.
            </div>
            <div className="footer-repo-link">
              <a
                href="https://github.com/PShreesh7/AI-Powered-Contract-Intelligence-Risk-Scoring-NLP-"
                target="_blank"
                rel="noreferrer"
                className="repo-link"
              >
                GitHub Repository &bull; Open Architecture
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
