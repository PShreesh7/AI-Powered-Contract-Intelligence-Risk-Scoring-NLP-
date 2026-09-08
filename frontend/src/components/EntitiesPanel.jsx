import { useState } from 'react';
import {
  Building2,
  User,
  Calendar,
  DollarSign,
  MapPin,
  Tag,
  Copy,
  Check,
  Sparkles,
} from 'lucide-react';
import Card3D from './Card3D.jsx';

const ENTITY_GROUPS = [
  {
    types: ['ORG', 'PARTY'],
    label: 'Organizations & Contracting Parties',
    color: '#818cf8',
    Icon: Building2,
    chipClass: 'ORG',
  },
  {
    types: ['PERSON'],
    label: 'Signatories & Named Persons',
    color: '#c084fc',
    Icon: User,
    chipClass: 'PERSON',
  },
  {
    types: ['DATE', 'TIME'],
    label: 'Dates & Deadlines',
    color: '#38bdf8',
    Icon: Calendar,
    chipClass: 'DATE',
  },
  {
    types: ['MONEY', 'PERCENT'],
    label: 'Monetary & Financial Values',
    color: '#34d399',
    Icon: DollarSign,
    chipClass: 'MONEY',
  },
  {
    types: ['GPE', 'LOC', 'FAC'],
    label: 'Jurisdictions & Applicable Law',
    color: '#fb923c',
    Icon: MapPin,
    chipClass: 'GPE',
  },
];

function dedupeEntities(list) {
  const seen = new Set();
  return list.filter((e) => {
    const key = `${e.label}::${e.text?.toLowerCase().trim()}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export default function EntitiesPanel({ entities = [] }) {
  const [copiedText, setCopiedText] = useState(null);

  if (!entities.length) {
    return (
      <div className="entities-empty-card">
        <Tag size={32} className="empty-tag-icon" />
        <p>No named entities were extracted from this contract.</p>
      </div>
    );
  }

  const deduped = dedupeEntities(entities);

  const grouped = ENTITY_GROUPS.map((group) => ({
    ...group,
    items: deduped.filter((e) => group.types.includes(e.label?.toUpperCase())),
  })).filter((g) => g.items.length > 0);

  const coveredTypes = new Set(ENTITY_GROUPS.flatMap((g) => g.types));
  const others = deduped.filter((e) => !coveredTypes.has(e.label?.toUpperCase()));

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopiedText(text);
    setTimeout(() => setCopiedText(null), 1800);
  };

  return (
    <div className="entities-panel-3d">
      <div className="entities-summary-banner">
        <Sparkles size={16} className="text-accent" />
        <span>
          <strong>{deduped.length} Key Legal Entities</strong> verified across 5 entity taxonomies
        </span>
      </div>

      <div className="entities-groups-grid">
        {grouped.map((group) => {
          const Icon = group.Icon;
          return (
            <Card3D key={group.label} className="entity-group-card-3d" maxTilt={4} scale={1.005}>
              <div className="group-card-header">
                <div
                  className="group-icon-pod"
                  style={{
                    color: group.color,
                    background: `${group.color}15`,
                    borderColor: `${group.color}35`,
                  }}
                >
                  <Icon size={16} />
                </div>
                <div className="group-card-title">{group.label}</div>
                <div className="group-card-badge" style={{ color: group.color, borderColor: `${group.color}40` }}>
                  {group.items.length}
                </div>
              </div>

              <div className="group-chips-wrap">
                {group.items.map((item, idx) => (
                  <button
                    type="button"
                    key={`${item.label}-${idx}`}
                    className={`entity-chip-3d ${copiedText === item.text ? 'is-copied' : ''}`}
                    onClick={() => handleCopy(item.text)}
                    title={`Click to copy: ${item.text}`}
                  >
                    <span className="chip-text">{item.text}</span>
                    {copiedText === item.text ? (
                      <Check size={12} className="chip-action-icon text-success" />
                    ) : (
                      <Copy size={11} className="chip-action-icon" />
                    )}
                  </button>
                ))}
              </div>
            </Card3D>
          );
        })}

        {others.length > 0 && (
          <Card3D className="entity-group-card-3d" maxTilt={4}>
            <div className="group-card-header">
              <div className="group-icon-pod text-muted">
                <Tag size={16} />
              </div>
              <div className="group-card-title">Miscellaneous Annotations</div>
              <div className="group-card-badge">{others.length}</div>
            </div>
            <div className="group-chips-wrap">
              {others.map((item, idx) => (
                <button
                  type="button"
                  key={`other-${idx}`}
                  className={`entity-chip-3d ${copiedText === item.text ? 'is-copied' : ''}`}
                  onClick={() => handleCopy(item.text)}
                  title={`Click to copy: ${item.text}`}
                >
                  <span className="chip-text">{item.text}</span>
                  {copiedText === item.text ? (
                    <Check size={12} className="chip-action-icon text-success" />
                  ) : (
                    <Copy size={11} className="chip-action-icon" />
                  )}
                </button>
              ))}
            </div>
          </Card3D>
        )}
      </div>
    </div>
  );
}
