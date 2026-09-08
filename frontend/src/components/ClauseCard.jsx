import { useState } from 'react';
import {
  ShieldAlert,
  Shield,
  FileText,
  Lock,
  RefreshCw,
  Scale,
  Lightbulb,
  BookOpen,
  ChevronDown,
  Copy,
  Check,
  Sparkles,
} from 'lucide-react';
import Card3D from './Card3D.jsx';

const CLAUSE_ICONS = {
  indemnification: ShieldAlert,
  termination: FileText,
  limitation_of_liability: Lock,
  auto_renewal: RefreshCw,
  dispute_resolution: Scale,
  confidentiality: Lock,
  intellectual_property: Lightbulb,
  governing_law: BookOpen,
  payment_terms: Scale,
  non_compete: Shield,
};

function getClauseIcon(type) {
  const normalized = (type ?? '').toLowerCase().replace(/ /g, '_');
  return CLAUSE_ICONS[normalized] ?? FileText;
}

export default function ClauseCard({ clause, isSelected, onSelect }) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const IconComponent = getClauseIcon(clause.clauseType);

  const handleCardClick = (e) => {
    // Avoid re-toggling if clicking copy button
    if (e.target.closest('.copy-btn')) return;
    onSelect(clause.id);
    setExpanded((prev) => !prev);
  };

  const handleCopySuggestion = (e) => {
    e.stopPropagation();
    if (clause.suggestion) {
      navigator.clipboard.writeText(clause.suggestion);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const riskColor =
    clause.risk === 'high'
      ? '#ff4d4d'
      : clause.risk === 'medium'
      ? '#ffa600'
      : '#00e699';

  const riskGlow =
    clause.risk === 'high'
      ? 'rgba(255, 77, 77, 0.25)'
      : clause.risk === 'medium'
      ? 'rgba(255, 166, 0, 0.22)'
      : 'rgba(0, 230, 153, 0.18)';

  return (
    <Card3D
      className={`clause-card-3d risk-${clause.risk} ${isSelected ? 'is-selected' : ''}`}
      maxTilt={5}
      scale={1.01}
      onClick={handleCardClick}
      style={{
        borderLeft: `4px solid ${riskColor}`,
        boxShadow: isSelected
          ? `0 12px 30px rgba(0, 0, 0, 0.5), 0 0 20px ${riskGlow}`
          : '0 4px 18px rgba(0, 0, 0, 0.35)',
      }}
      role="button"
      tabIndex={0}
      aria-expanded={expanded}
      onKeyDown={(e) => e.key === 'Enter' && handleCardClick(e)}
    >
      {/* Card Header */}
      <div className="clause-3d-header">
        <div
          className="clause-icon-wrap"
          style={{ background: `${riskColor}18`, color: riskColor, borderColor: `${riskColor}44` }}
        >
          <IconComponent size={18} />
        </div>

        <div className="clause-title-wrap">
          <div className="clause-name">{clause.label}</div>
          <div className="clause-category-tag">{clause.clauseType}</div>
        </div>

        <div className="clause-badge-wrap">
          <span
            className="risk-pill"
            style={{
              background: `${riskColor}18`,
              borderColor: `${riskColor}44`,
              color: riskColor,
              boxShadow: `0 0 8px ${riskColor}33`,
            }}
          >
            {clause.risk === 'medium' ? 'MED RISK' : `${clause.risk.toUpperCase()} RISK`}
          </span>
          <ChevronDown
            size={18}
            className={`chevron-icon ${expanded ? 'rotated' : ''}`}
          />
        </div>
      </div>

      {/* Progress Bar */}
      <div className="clause-meter-bar">
        <div
          className="clause-meter-fill"
          style={{
            width: `${clause.riskScore}%`,
            background: `linear-gradient(90deg, ${riskColor}88, ${riskColor})`,
            boxShadow: `0 0 10px ${riskColor}aa`,
          }}
        />
      </div>

      {/* Rationale Excerpt */}
      <p className="clause-brief">{clause.rationale}</p>

      {/* Expanded Details */}
      {expanded && (
        <div className="clause-expand-body">
          <div className="clause-quote-box">
            <span className="quote-label">CONTRACT EXCERPT:</span>
            <p className="quote-content">
              "{clause.text?.slice(0, 280)}
              {clause.text?.length > 280 ? '…' : ''}"
            </p>
          </div>

          {clause.suggestion && (
            <div className="clause-suggestion-box">
              <div className="sugg-header">
                <div className="sugg-title">
                  <Sparkles size={14} className="sparkle-icon" />
                  <span>AI Legal Remediation Suggestion</span>
                </div>
                <button
                  type="button"
                  className="copy-btn"
                  onClick={handleCopySuggestion}
                  title="Copy suggestion to clipboard"
                >
                  {copied ? (
                    <>
                      <Check size={13} />
                      <span>Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy size={13} />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>
              <p className="sugg-text">{clause.suggestion}</p>
            </div>
          )}

          <div className="clause-footer-meta">
            <div className="meta-confidence">
              <span>Model Confidence:</span>
              <strong>{Math.round((clause.confidence ?? 0) * 100)}%</strong>
              <div className="confidence-track">
                <div
                  className="confidence-fill"
                  style={{ width: `${Math.round((clause.confidence ?? 0) * 100)}%` }}
                />
              </div>
            </div>
            <div className="meta-offsets">
              <span>Chars {clause.startOffset}–{clause.endOffset}</span>
            </div>
          </div>
        </div>
      )}
    </Card3D>
  );
}
