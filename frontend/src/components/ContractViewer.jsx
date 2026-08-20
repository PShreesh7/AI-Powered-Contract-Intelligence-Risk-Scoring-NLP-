// Splits the full contract text into plain and highlighted segments
// based on clause offsets, so risky clauses are highlighted directly
// in the document — the way a reviewer would mark up a paper copy.

function buildSegments(fullText, clauses) {
  const sorted = [...clauses].sort((a, b) => a.startOffset - b.startOffset);
  const segments = [];
  let cursor = 0;

  for (const clause of sorted) {
    if (clause.startOffset > cursor) {
      segments.push({ type: 'plain', text: fullText.slice(cursor, clause.startOffset) });
    }
    segments.push({
      type: 'clause',
      text: fullText.slice(clause.startOffset, clause.endOffset),
      clause
    });
    cursor = clause.endOffset;
  }
  if (cursor < fullText.length) {
    segments.push({ type: 'plain', text: fullText.slice(cursor) });
  }
  return segments;
}

export default function ContractViewer({ fullText, clauses, selectedClauseId, onSelectClause }) {
  if (!fullText) {
    return (
      <div className="viewer-empty">
        <p>Upload a contract to see it laid out here, with risky clauses highlighted inline.</p>
      </div>
    );
  }

  const segments = buildSegments(fullText, clauses);

  return (
    <div className="viewer-paper">
      <p className="viewer-text">
        {segments.map((seg, i) =>
          seg.type === 'plain' ? (
            <span key={i}>{seg.text}</span>
          ) : (
            <mark
              key={i}
              id={`clause-${seg.clause.id}`}
              className={`highlight risk-${seg.clause.risk} ${selectedClauseId === seg.clause.id ? 'is-selected' : ''}`}
              onClick={() => onSelectClause(seg.clause.id)}
              title={seg.clause.label}
            >
              {seg.text}
            </mark>
          )
        )}
      </p>
    </div>
  );
}
