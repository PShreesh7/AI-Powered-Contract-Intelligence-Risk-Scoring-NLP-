import { FileText, ShieldAlert, AlertTriangle, ShieldCheck, Check } from 'lucide-react';

function buildSegments(fullText, clauses) {
  if (!fullText) return [];
  const sorted = [...clauses]
    .filter((c) => c.startOffset >= 0 && c.endOffset <= fullText.length)
    .sort((a, b) => a.startOffset - b.startOffset);

  const segments = [];
  let cursor = 0;

  for (const clause of sorted) {
    if (clause.startOffset > cursor) {
      segments.push({ type: 'plain', text: fullText.slice(cursor, clause.startOffset) });
    }
    if (clause.startOffset >= cursor) {
      segments.push({
        type: 'clause',
        text: fullText.slice(clause.startOffset, clause.endOffset),
        clause,
      });
      cursor = clause.endOffset;
    }
  }
  if (cursor < fullText.length) {
    segments.push({ type: 'plain', text: fullText.slice(cursor) });
  }
  return segments;
}

export default function ContractViewer({
  fullText,
  clauses = [],
  filename,
  selectedClauseId,
  onSelectClause,
}) {
  if (!fullText) {
    return (
      <div className="viewer-empty-state">
        <FileText size={36} className="empty-file-icon" />
        <p className="viewer-empty-text">
          Upload a contract to view the full text marked with color-coded risk clauses.
        </p>
      </div>
    );
  }

  const segments = buildSegments(fullText, clauses);

  return (
    <div className="viewer-paper-3d">
      {/* Document Meta Header */}
      <div className="doc-top-bar">
        <div className="doc-name-badge">
          <FileText size={16} className="text-accent" />
          <span className="doc-name">{filename}</span>
        </div>

        {/* Legend */}
        <div className="doc-legend">
          <div className="legend-item text-danger">
            <span className="legend-indicator bg-danger" />
            <span>High Risk</span>
          </div>
          <div className="legend-item text-warning">
            <span className="legend-indicator bg-warning" />
            <span>Medium Risk</span>
          </div>
          <div className="legend-item text-success">
            <span className="legend-indicator bg-success" />
            <span>Low Risk</span>
          </div>
        </div>

        <div className="doc-clause-count">
          <span>{clauses.length} Provisions Detected</span>
        </div>
      </div>

      {/* Main Document Body */}
      <div className="doc-parchment-body">
        <div className="doc-text-flow" role="document">
          {segments.map((seg, idx) =>
            seg.type === 'plain' ? (
              <span key={idx} className="plain-run">
                {seg.text}
              </span>
            ) : (
              <mark
                key={idx}
                id={`clause-${seg.clause.id}`}
                className={`clause-highlight risk-${seg.clause.risk} ${
                  selectedClauseId === seg.clause.id ? 'is-active-clause' : ''
                }`}
                onClick={() => onSelectClause(seg.clause.id)}
                title={`${seg.clause.label} · ${seg.clause.risk.toUpperCase()} RISK`}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && onSelectClause(seg.clause.id)}
              >
                <span className="clause-marker-badge">{seg.clause.label}</span>
                {seg.text}
              </mark>
            )
          )}
        </div>
      </div>
    </div>
  );
}
