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
  Zap,
  ArrowRight,
  AlertCircle,
} from 'lucide-react';
import Card3D from './Card3D.jsx';

const FEATURES = [
  {
    icon: Cpu,
    color: '#d4a843',
    title: 'Legal Entity Extraction',
    desc: 'Extracts signing parties, effective dates, governing jurisdictions, and monetary values via fine-tuned spaCy NLP.',
  },
  {
    icon: ShieldCheck,
    color: '#ff4d4d',
    title: '41+ Clause Classification',
    desc: 'Automatically parses and classifies indemnification, liability caps, non-competes, and termination provisions.',
  },
  {
    icon: MessageSquareCode,
    color: '#38bdf8',
    title: 'Grounded Contract Q&A',
    desc: 'Chat directly with your contract using Gemini LLM. Get plain-language explanations with clause-grounded citations.',
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

  return (
    <div className="landing-cinematic">
      {/* Top Navbar */}
      <nav className="landing-topbar">
        <div className="landing-brand">
          <div className="brand-logo-gem">
            <Scale size={20} className="gem-icon" />
            <div className="gem-glow" />
          </div>
          <span className="brand-name">
            Lex<span className="brand-ai">AI</span>
          </span>
        </div>
        <div className="landing-nav-badge">
          <span className="badge-pulse" />
          <span>NLP CONTRACT INTELLIGENCE</span>
        </div>
      </nav>

      {/* Main Content */}
      <div className="landing-stage">
        {/* Eyebrow badge */}
        <div className="cinematic-badge">
          <Sparkles size={14} className="sparkle-anim" />
          <span>NEXT-GEN LEGAL LANGUAGE MODEL PIPELINE</span>
        </div>

        {/* Hero Headlines */}
        <h1 className="cinematic-title">
          Autonomous Intelligence for<br />
          <span className="cinematic-gradient-text">Complex Legal Contracts</span>
        </h1>

        <p className="cinematic-subtitle">
          Instantly ingest PDF & Word agreements. Extract key parties, segment provisions,
          detect red-flag clauses, and run grounded AI chat in seconds.
        </p>

        {/* Error Notification */}
        {error && (
          <div className="landing-error-banner">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {/* 3D Holographic Upload Zone */}
        <Card3D
          className={`upload-zone-3d ${isDragOver ? 'is-drag-over' : ''}`}
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

          {/* Laser Scanner Line */}
          <div className="scanner-line" />

          <div className="upload-icon-ring">
            <UploadCloud size={32} className="upload-cloud-icon" />
          </div>

          <div className="upload-prompt">
            <span className="primary-prompt">Drop contract here or click to browse</span>
            <span className="secondary-prompt">Supports PDF, Word (.docx), and plain text documents</span>
          </div>

          <div className="upload-filetypes">
            <span className="ft-badge">PDF DOCUMENT</span>
            <span className="ft-badge">DOCX WORD</span>
            <span className="ft-badge">TXT CONTRACT</span>
          </div>
        </Card3D>

        {/* One-Click Quick Demo Contracts */}
        <div className="demo-launcher-bar">
          <span className="demo-hint">Or test instantly with pre-loaded demo contracts:</span>
          <div className="demo-btns-wrap">
            <button
              type="button"
              className="btn-demo-pill"
              disabled={demoLoading !== null}
              onClick={() => handleLoadDemo('pdf')}
            >
              <FileText size={15} className="demo-icon" />
              <span>{demoLoading === 'pdf' ? 'Loading…' : 'Try Master Service Agreement (PDF)'}</span>
              <ArrowRight size={13} className="arrow-icon" />
            </button>

            <button
              type="button"
              className="btn-demo-pill"
              disabled={demoLoading !== null}
              onClick={() => handleLoadDemo('docx')}
            >
              <FileCheck2 size={15} className="demo-icon" />
              <span>{demoLoading === 'docx' ? 'Loading…' : 'Try Consulting NDA (DOCX)'}</span>
              <ArrowRight size={13} className="arrow-icon" />
            </button>
          </div>
        </div>

        {/* 3D Feature Grid */}
        <div className="cinematic-features-grid">
          {FEATURES.map((feat, idx) => {
            const Icon = feat.icon;
            return (
              <Card3D key={idx} className="cinematic-feature-card" maxTilt={8}>
                <div
                  className="feat-icon-pod"
                  style={{
                    color: feat.color,
                    background: `${feat.color}15`,
                    borderColor: `${feat.color}40`,
                  }}
                >
                  <Icon size={22} />
                </div>
                <h3 className="feat-title">{feat.title}</h3>
                <p className="feat-desc">{feat.desc}</p>
              </Card3D>
            );
          })}
        </div>
      </div>
    </div>
  );
}
