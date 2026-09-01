/**
 * ContractViewer — renders the full contract text with color-coded
 * clause highlights inline. Clicking a highlight selects that clause.
 * Matches the design of a paper markup — colored underlines for risk level.
 */

const CLAUSE_ICONS = {
  indemnification:      '🛡️',
  termination:          '⏹️',
  limitation_of_liability: '🔒',
  auto_renewal:         '🔄',
  dispute_resolution:   '⚖️',
  confidentiality:      '🔏',
  intellectual_property: '💡',
  governing_law:        '📜',
  default: '📌',
};

function buildSegments(fullText, clauses) {
  if (!fullText) return [];
  const sorted = [...clauses]
    .filter(c => c.startOffset >= 0 && c.endOffset <= fullText.length)
    .sort((a, b) => a.startOffset - b.startOffset);

  const segments = [];
  let cursor = 0;

  for (const clause of sorted) {
    if (clause.startOffset > cursor) {
      segments.push({ type: 'plain', text: fullText.slice(cursor, clause.startOffset) });
    }
    if (clause.startOffset >= cursor) {
      segments.push({ type: 'clause', text: fullText.slice(clause.startOffset, clause.endOffset), clause });
      cursor = clause.endOffset;
    }
  }
  if (cursor < fullText.length) {
    segments.push({ type: 'plain', text: fullText.slice(cursor) });
  }
  return segments;
}

export default function ContractViewer({ fullText, clauses, filename, selectedClauseId, onSelectClause }) {
  if (!fullText) {
    return (
      <div className="viewer-empty-state">
        <div className="viewer-empty-icon">📄</div>
        <p className="viewer-empty-text">
          Upload a contract to see the full text here with risk clauses highlighted inline.
        </p>
      </div>
    );
  }

  const segments = buildSegments(fullText, clauses);

  return (
    <div className="viewer-paper">
      <div className="viewer-doc-title">
        <span>📄</span>
        <span>{filename}</span>
        <span style={{ marginLeft: 'auto', fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-muted)' }}>
          {clauses.length} clauses detected
        </span>
      </div>

      {/* Legend */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', flexWrap: 'wrap' }}>
        {[
          { risk: 'high',   label: 'High Risk' },
          { risk: 'medium', label: 'Medium Risk' },
          { risk: 'low',    label: 'Low Risk' },
        ].map(({ risk, label }) => (
          <div key={risk} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span
              style={{
                display: 'inline-block',
                width: '20px',
                height: '3px',
                background: `var(--risk-${risk === 'medium' ? 'med' : risk})`,
                borderRadius: '2px',
              }}
            />
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{label}</span>
          </div>
        ))}
      </div>

      <p className="viewer-text" role="document">
        {segments.map((seg, i) =>
          seg.type === 'plain' ? (
            <span key={i}>{seg.text}</span>
          ) : (
            <mark
              key={i}
              id={`clause-${seg.clause.id}`}
              className={`clause-mark risk-${seg.clause.risk} ${selectedClauseId === seg.clause.id ? 'is-selected' : ''}`}
              onClick={() => onSelectClause(seg.clause.id)}
              title={`${CLAUSE_ICONS[seg.clause.clauseType] ?? CLAUSE_ICONS.default} ${seg.clause.label} — ${seg.clause.risk} risk`}
              role="button"
              tabIndex={0}
              aria-label={`${seg.clause.label}: ${seg.clause.risk} risk clause`}
              onKeyDown={e => e.key === 'Enter' && onSelectClause(seg.clause.id)}
            >
              {seg.text}
            </mark>
          )
        )}
      </p>
    </div>
  );
}
