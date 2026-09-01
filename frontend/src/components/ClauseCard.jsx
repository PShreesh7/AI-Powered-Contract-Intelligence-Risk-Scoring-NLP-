import { useState } from 'react';

const CLAUSE_ICONS = {
  indemnification:         '🛡️',
  termination:             '⏹️',
  limitation_of_liability: '🔒',
  auto_renewal:            '🔄',
  dispute_resolution:      '⚖️',
  confidentiality:         '🔏',
  intellectual_property:   '💡',
  governing_law:           '📜',
};

function getIcon(clauseType) {
  return CLAUSE_ICONS[clauseType?.toLowerCase()] ?? '📌';
}

export default function ClauseCard({ clause, isSelected, onSelect }) {
  const [expanded, setExpanded] = useState(false);

  function handleClick() {
    onSelect(clause.id);
    setExpanded(e => !e);
  }

  const fillWidth = `${clause.riskScore}%`;

  return (
    <li
      className={`clause-card risk-${clause.risk} ${isSelected ? 'is-selected' : ''}`}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      aria-expanded={expanded}
      aria-label={`${clause.label}: ${clause.risk} risk, score ${clause.riskScore}`}
      onKeyDown={e => e.key === 'Enter' && handleClick()}
    >
      {/* Header row */}
      <div className="clause-card-header">
        <span className="clause-type-icon" aria-hidden="true">{getIcon(clause.clauseType)}</span>
        <span className="clause-label">{clause.label}</span>
        <span className={`risk-badge risk-${clause.risk}`}>
          {clause.risk === 'medium' ? 'Med' : clause.risk.charAt(0).toUpperCase() + clause.risk.slice(1)}
        </span>
      </div>

      {/* Score bar */}
      <div className="clause-score-bar" role="progressbar" aria-valuenow={clause.riskScore} aria-valuemin={0} aria-valuemax={100}>
        <div className="clause-score-fill" style={{ width: fillWidth }} />
      </div>

      {/* Rationale */}
      <div className="clause-card-body">
        <p className="clause-rationale">{clause.rationale}</p>

        {/* Expanded detail */}
        {expanded && (
          <div className="clause-expand">
            <div className="clause-text-excerpt">
              "{clause.text?.slice(0, 220)}{clause.text?.length > 220 ? '…' : ''}"
            </div>

            {clause.suggestion && (
              <div className="clause-suggestion">
                <span className="suggestion-icon">💡</span>
                <span>{clause.suggestion}</span>
              </div>
            )}

            <div className="clause-confidence">
              Model confidence: {Math.round((clause.confidence ?? 0) * 100)}%
            </div>
          </div>
        )}
      </div>
    </li>
  );
}
