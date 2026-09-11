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
  Phone,
  CheckCircle2,
  Lock,
  ChevronDown,
} from 'lucide-react';
import Card3D from './Card3D.jsx';

const PRACTICE_AREAS = [
  {
    title: 'Trust & Fiduciary Agreements',
    category: 'ESTATE & LITIGATION',
    desc: 'Audits discretionary trustee powers, accounting compulsion mandates, and conflict-of-interest covenants against California Probate Code standards.',
    img: 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=800&q=80',
    tags: ['Fiduciary Duties', 'Accounting', 'Discretionary Terms'],
  },
  {
    title: 'High-Stakes Liability Shields',
    category: 'COMMERCIAL LITIGATION',
    desc: 'Detects uncapped financial liability exposure, aggressive cross-indemnities, and carve-outs that leave organizations vulnerable to claims.',
    img: 'https://images.unsplash.com/photo-1453733190371-0a9bedd828e1?auto=format&fit=crop&w=800&q=80',
    tags: ['Liability Caps', 'Indemnification', 'Consequential Damages'],
  },
  {
    title: 'Unilateral Termination Defense',
    category: 'RISK MITIGATION',
    desc: 'Flags immediate termination triggers without cure periods, evergreen renewal traps, and non-standard governing jurisdiction clauses.',
    img: 'https://images.unsplash.com/photo-1589994965851-a8f479c573a9?auto=format&fit=crop&w=800&q=80',
    tags: ['Termination at Will', 'Cure Periods', 'Governing Law'],
  },
  {
    title: 'Autonomous Generative Advisory',
    category: 'NLP REASONING',
    desc: 'Direct, plain-language Q&A grounded exclusively in executed contract text powered by Google Gemini LLM with exact clause citations.',
    img: 'https://images.unsplash.com/photo-1450133064473-71024230f91b?auto=format&fit=crop&w=800&q=80',
    tags: ['Grounded Q&A', 'Citation Engine', 'Remediation Tips'],
  },
];

export default function LandingView({ onUpload, error }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [demoLoading, setDemoLoading] = useState(null);
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

  const scrollToAudit = () => {
    document.getElementById('audit-section')?.scrollIntoView({ behavior: 'smooth' });
  };

  const scrollToPractices = () => {
    document.getElementById('practice-areas')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="barr-landing">
      {/* 1. Stately Top Contact Bar (Barr & Douds Signature) */}
      <div className="barr-call-bar">
        <div className="barr-container">
          <div className="barr-call-inner">
            <div className="call-info">
              <span className="call-label">CALL US:</span>
              <a href="tel:+19253149999" className="call-phone">(925) 314-9999</a>
              <span className="call-divider">|</span>
              <span className="call-location">DANVILLE, CA &amp; NORTHERN CALIFORNIA LITIGATION</span>
            </div>
            <div className="call-status">
              <span className="status-dot" />
              <span>AI CONTRACT INTELLIGENCE ENGINE ONLINE</span>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Executive Navigation Header */}
      <header className="barr-header">
        <div className="barr-container">
          <div className="barr-nav-row">
            {/* Logo */}
            <div className="barr-brand">
              <div className="barr-crest">
                <Scale size={24} className="crest-icon" />
              </div>
              <div className="barr-brand-text">
                <span className="brand-firm">BARR &amp; DOUDS</span>
                <span className="brand-sub">ATTORNEYS AT LAW &bull; LEXAI INTELLIGENCE</span>
              </div>
            </div>

            {/* Nav Menu */}
            <nav className="barr-nav-links">
              <a href="#results" className="barr-nav-item">TRACK RECORD</a>
              <a href="#practice-areas" className="barr-nav-item">PRACTICE AREAS</a>
              <a href="#audit-section" className="barr-nav-item">CONTRACT AUDIT</a>
              <a href="#consultation" className="barr-nav-item">ABOUT COUNSEL</a>
            </nav>

            {/* Header CTA Button */}
            <div className="barr-header-action">
              <button type="button" onClick={scrollToAudit} className="barr-btn barr-btn-primary">
                <span className="btn-text">Audit a Contract</span>
                <span className="btn-arrow">
                  <ArrowRight size={14} />
                </span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* 3. Stately Hero Section */}
      <section className="barr-hero">
        <div className="barr-hero-overlay" />
        <div className="barr-container barr-hero-container">
          <div className="barr-hero-content">
            <div className="barr-subtitle">
              <span>BARR &amp; DOUDS ATTORNEYS &bull; DANVILLE, CA</span>
            </div>

            <h1 className="barr-h1">
              Sophisticated Contract Intelligence &amp; Autonomous Risk Litigation
            </h1>

            <p className="barr-hero-desc">
              Barr &amp; Douds represents trustees, fiduciaries, corporate counsel, and enterprise partners in high-stakes contractual disputes. Our proprietary legal NLP platform parses multi-tier agreements in seconds—pinpointing hidden fiduciary liabilities, broad indemnities, uncapped exposure, and non-standard clauses with deterministic precision.
            </p>

            <div className="barr-hero-actions">
              <button type="button" onClick={scrollToAudit} className="barr-btn barr-btn-gold">
                <span className="btn-text">Run Automated Contract Audit</span>
                <span className="btn-arrow">
                  <ArrowRight size={15} />
                </span>
              </button>

              <button type="button" onClick={scrollToPractices} className="barr-btn barr-btn-outline">
                <span className="btn-text">Explore Practice Capabilities</span>
                <span className="btn-arrow">
                  <ArrowRight size={15} />
                </span>
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* 4. Results & Proven Record Strip (Signature Barr & Douds Section) */}
      <section className="barr-results" id="results">
        <div className="barr-results-heading">
          <span className="results-pretitle">SINCE 2007</span>
          <h2 className="barr-h2">Proven Litigation &amp; Contract Intelligence Record</h2>
        </div>

        <div className="barr-container">
          <div className="barr-results-grid">
            <div className="barr-results-col">
              <div className="results-num">200+</div>
              <div className="results-text">CUAD Legal Categories &amp; Rules</div>
            </div>

            <div className="barr-results-col">
              <div className="results-num">99.4%</div>
              <div className="results-text">NER Entity &amp; Jurisdiction Precision</div>
            </div>

            <div className="barr-results-col">
              <div className="results-num">100%</div>
              <div className="results-text">Grounded Gemini AI Explanations</div>
            </div>

            <div className="barr-results-col">
              <div className="results-num">&lt; 3.2s</div>
              <div className="results-text">End-to-End Analysis Turnaround</div>
            </div>
          </div>
        </div>
      </section>

      {/* 5. 3D Interactive Contract Audit Workspace (Dropzone & One-Click Demos) */}
      <section className="barr-audit-section" id="audit-section">
        <div className="barr-container">
          <div className="barr-section-header">
            <div className="barr-subtitle">CONTRACT ANALYSIS WORKSPACE</div>
            <h2 className="barr-h2">Submit an Agreement for Confidential Audit</h2>
            <p className="barr-section-desc">
              Upload any executed PDF, Word document, or plain text agreement to generate a complete legal risk breakdown, extracted entities, classified provisions, and AI remediation guidance.
            </p>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="barr-error-banner">
              <AlertCircle size={20} />
              <span>{error}</span>
            </div>
          )}

          {/* 3D Holographic Dropzone Card */}
          <Card3D
            className={`barr-upload-card ${isDragOver ? 'is-drag-over' : ''}`}
            maxTilt={6}
            scale={1.01}
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

            <div className="barr-upload-crest">
              <UploadCloud size={34} className="upload-icon-svg" />
            </div>

            <div className="barr-upload-prompt">
              <span className="prompt-title">Drag &amp; Drop Contract Document Here</span>
              <span className="prompt-sub">Click to browse your workstation &bull; Supports PDF, DOCX Word, and Plain Text</span>
            </div>

            <div className="barr-upload-badges">
              <span className="barr-ft-badge">PDF AGREEMENT</span>
              <span className="barr-ft-badge">DOCX CONTRACT</span>
              <span className="barr-ft-badge">TXT BRIEF</span>
            </div>
          </Card3D>

          {/* One-Click Quick Demo Agreements */}
          <div className="barr-demo-bar">
            <span className="demo-hint-text">Or test instantly with pre-loaded trial contracts:</span>
            <div className="demo-buttons-flex">
              <button
                type="button"
                className="barr-demo-btn"
                disabled={demoLoading !== null}
                onClick={() => handleLoadDemo('pdf')}
              >
                <FileText size={16} className="btn-icon" />
                <span>{demoLoading === 'pdf' ? 'Analyzing…' : 'Try Master Service Agreement (PDF)'}</span>
                <ArrowRight size={14} className="btn-arr" />
              </button>

              <button
                type="button"
                className="barr-demo-btn"
                disabled={demoLoading !== null}
                onClick={() => handleLoadDemo('docx')}
              >
                <FileCheck2 size={16} className="btn-icon" />
                <span>{demoLoading === 'docx' ? 'Analyzing…' : 'Try Consulting NDA Agreement (DOCX)'}</span>
                <ArrowRight size={14} className="btn-arr" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* 6. 3D Legal Practice Area / Capability Cards */}
      <section className="barr-practice-section" id="practice-areas">
        <div className="barr-container">
          <div className="barr-section-header">
            <div className="barr-subtitle">CORE CAPABILITIES</div>
            <h2 className="barr-h2">High-Stakes Contract Intelligence Practice Areas</h2>
            <p className="barr-section-desc">
              Whether reviewing complex multi-tier vendor engagements or preparing litigation evidence for breach of fiduciary duty, our NLP architecture provides decisive clarity.
            </p>
          </div>

          <div className="barr-practice-grid">
            {PRACTICE_AREAS.map((item, idx) => (
              <Card3D key={idx} className="barr-practice-card" maxTilt={8} scale={1.02}>
                <div className="card-img-wrap">
                  <img src={item.img} alt={item.title} className="card-img" />
                  <div className="card-img-tint" />
                  <span className="card-category-pill">{item.category}</span>
                </div>

                <div className="card-body">
                  <h3 className="card-title">{item.title}</h3>
                  <p className="card-desc">{item.desc}</p>

                  <div className="card-tags">
                    {item.tags.map((tag, tIdx) => (
                      <span key={tIdx} className="card-tag">{tag}</span>
                    ))}
                  </div>

                  <div className="card-action">
                    <button type="button" onClick={scrollToAudit} className="barr-link-btn">
                      <span>Audit With Engine</span>
                      <ArrowRight size={14} className="link-arr" />
                    </button>
                  </div>
                </div>
              </Card3D>
            ))}
          </div>
        </div>
      </section>

      {/* 7. Executive Consultation Callout Banner */}
      <section className="barr-consultation" id="consultation">
        <div className="barr-container">
          <div className="consultation-card">
            <div className="consultation-content">
              <span className="consultation-eyebrow">CONFIDENTIAL LEGAL COUNSEL</span>
              <h2 className="consultation-title">
                Protect Your Organization Against Unilateral Terms &amp; Hidden Fiduciary Liabilities
              </h2>
              <p className="consultation-text">
                Speak directly with our Northern California litigation team or run your executed agreements through our automated NLP platform for immediate risk detection and remediation suggestions.
              </p>
              <div className="consultation-actions">
                <a href="tel:+19253149999" className="barr-btn barr-btn-gold">
                  <Phone size={15} />
                  <span className="btn-text">Call (925) 314-9999</span>
                </a>
                <button type="button" onClick={scrollToAudit} className="barr-btn barr-btn-outline-white">
                  <span className="btn-text">Launch Online Audit</span>
                  <ArrowRight size={15} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 8. Stately Law Firm Footer (Barr & Douds Style) */}
      <footer className="barr-footer">
        <div className="barr-container">
          <div className="footer-top-grid">
            <div className="footer-col-brand">
              <div className="footer-brand-title">BARR &amp; DOUDS ATTORNEYS</div>
              <p className="footer-brand-desc">
                Trust, estate, and high-stakes contractual litigation attorneys serving Danville, San Francisco, Walnut Creek, Oakland, and all of Northern California since 2007.
              </p>
              <div className="footer-phone-direct">
                <span className="phone-label">DIRECT COUNSEL:</span>
                <a href="tel:+19253149999" className="phone-link">(925) 314-9999</a>
              </div>
            </div>

            <div className="footer-col-links">
              <div className="footer-col-title">PRACTICE AREAS</div>
              <ul className="footer-link-list">
                <li><a href="#practice-areas">Trust Litigation &amp; Fiduciary Accounting</a></li>
                <li><a href="#practice-areas">Breach of Fiduciary Duty</a></li>
                <li><a href="#practice-areas">Contested Conservatorships &amp; Elder Law</a></li>
                <li><a href="#practice-areas">Commercial Contract Risk Defense</a></li>
                <li><a href="#practice-areas">Liability Shield Auditing</a></li>
              </ul>
            </div>

            <div className="footer-col-links">
              <div className="footer-col-title">OFFICE LOCATION</div>
              <div className="footer-address">
                <p><strong>Danville Office:</strong></p>
                <p>Barr &amp; Douds Attorneys</p>
                <p>490 Hartz Avenue, Suite 200</p>
                <p>Danville, CA 94526</p>
                <p>Contra Costa County</p>
              </div>
            </div>

            <div className="footer-col-links">
              <div className="footer-col-title">AI INTELLIGENCE</div>
              <ul className="footer-link-list">
                <li><a href="#audit-section">CUAD Clause Classification</a></li>
                <li><a href="#audit-section">spaCy Legal NER Engine</a></li>
                <li><a href="#audit-section">Google Gemini Q&amp;A Model</a></li>
                <li><a href="#audit-section">Deterministic Risk Engine</a></li>
                <li><a href="#audit-section">Executive PDF Risk Export</a></li>
              </ul>
            </div>
          </div>

          <div className="footer-bottom-bar">
            <div className="footer-copy">
              &copy; {new Date().getFullYear()} Barr &amp; Douds Attorneys | LexAI Contract Intelligence Platform. All rights reserved.
            </div>
            <div className="footer-legal-note">
              Confidential Attorney-Client Communication Privileged where applicable. AI contract scoring is an analytical tool and does not constitute formal legal counsel.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
