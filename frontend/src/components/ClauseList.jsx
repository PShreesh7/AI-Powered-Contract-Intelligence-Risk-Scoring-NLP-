const RISK_LABEL = { high: 'High', medium: 'Medium', low: 'Low' };

export default function ClauseList({ clauses, selectedClauseId, onSelectClause }) {
  if (!clauses?.length) return null;

  const ordered = [...clauses].sort((a, b) => b.riskScore - a.riskScore);

  return (
    <ul className="clause-list">
      {ordered.map((clause) => (
        <li
          key={clause.id}
          className={`clause-item ${selectedClauseId === clause.id ? 'is-selected' : ''}`}
          onClick={() => onSelectClause(clause.id)}
        >
          <div className="clause-item-top">
            <span className="clause-label">{clause.label}</span>
            <span className={`risk-badge risk-${clause.risk}`}>{RISK_LABEL[clause.risk]}</span>
          </div>
          <p className="clause-rationale">{clause.rationale}</p>
        </li>
      ))}
    </ul>
  );
}
