/**
 * EntitiesPanel — visualizes Named Entity Recognition (NER) output.
 * Groups entities by type and renders them as color-coded chips.
 */

const ENTITY_GROUPS = [
  { types: ['ORG', 'PARTY'],       label: 'Organizations / Parties', dot: 'var(--ent-party)',  chipClass: 'ORG' },
  { types: ['PERSON'],             label: 'Persons',                  dot: 'var(--ent-org)',    chipClass: 'PERSON' },
  { types: ['DATE', 'TIME'],       label: 'Dates & Timeframes',       dot: 'var(--ent-date)',   chipClass: 'DATE' },
  { types: ['MONEY', 'PERCENT'],   label: 'Monetary / Percentages',   dot: 'var(--ent-money)',  chipClass: 'MONEY' },
  { types: ['GPE', 'LOC', 'FAC'], label: 'Jurisdictions & Locations', dot: 'var(--ent-jur)',    chipClass: 'GPE' },
];

function dedupeEntities(list) {
  const seen = new Set();
  return list.filter(e => {
    const key = `${e.label}::${e.text?.toLowerCase().trim()}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export default function EntitiesPanel({ entities = [] }) {
  if (!entities.length) {
    return (
      <div className="entities-empty">
        <div style={{ fontSize: '32px', marginBottom: '8px' }}>🔍</div>
        <p>No named entities were extracted from this contract.</p>
      </div>
    );
  }

  const deduped = dedupeEntities(entities);

  // Build groups
  const grouped = ENTITY_GROUPS.map(group => ({
    ...group,
    items: deduped.filter(e => group.types.includes(e.label?.toUpperCase())),
  })).filter(g => g.items.length > 0);

  // Catch-all for unmatched entity types
  const coveredTypes = new Set(ENTITY_GROUPS.flatMap(g => g.types));
  const others = deduped.filter(e => !coveredTypes.has(e.label?.toUpperCase()));

  return (
    <div className="entities-panel">
      <div style={{ marginBottom: '20px' }}>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.6 }}>
          {deduped.length} unique named entities extracted by spaCy NER from this contract.
        </p>
      </div>

      {grouped.map(group => (
        <div key={group.label} className="entity-group">
          <div className="entity-group-header">
            <span className="entity-group-dot" style={{ background: group.dot }} />
            <span className="entity-group-name">{group.label}</span>
            <span className="entity-group-count">{group.items.length}</span>
          </div>
          <div className="entity-chips">
            {group.items.map((e, i) => (
              <span
                key={`${e.label}-${i}`}
                className={`entity-chip ${group.chipClass}`}
                title={`Entity type: ${e.label}`}
              >
                {e.text}
              </span>
            ))}
          </div>
        </div>
      ))}

      {others.length > 0 && (
        <div className="entity-group">
          <div className="entity-group-header">
            <span className="entity-group-dot" style={{ background: 'var(--ent-other)' }} />
            <span className="entity-group-name">Other</span>
            <span className="entity-group-count">{others.length}</span>
          </div>
          <div className="entity-chips">
            {others.map((e, i) => (
              <span
                key={`other-${i}`}
                className="entity-chip default"
                title={`Entity type: ${e.label}`}
              >
                {e.text}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
