// Signature element: the overall risk score rendered as a stamped
// circular seal — evoking a notary/authentication stamp rather than
// a generic dashboard gauge. A needle sweeps across a 240° arc from
// low (sage) through medium (amber) to high (brick) risk.

const START_ANGLE = -210; // degrees, 0 = pointing right
const SWEEP = 240;

function polarToCartesian(cx, cy, r, angleDeg) {
  const rad = (angleDeg * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function arcPath(cx, cy, r, startDeg, endDeg) {
  const start = polarToCartesian(cx, cy, r, startDeg);
  const end = polarToCartesian(cx, cy, r, endDeg);
  const largeArc = endDeg - startDeg <= 180 ? 0 : 1;
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 1 ${end.x} ${end.y}`;
}

function riskLabel(score) {
  if (score >= 70) return { text: 'High risk', color: 'var(--risk-high)' };
  if (score >= 40) return { text: 'Medium risk', color: 'var(--risk-med)' };
  return { text: 'Low risk', color: 'var(--risk-low)' };
}

export default function RiskGauge({ score = 0 }) {
  const cx = 100, cy = 100, r = 78;
  const needleAngle = START_ANGLE + (SWEEP * score) / 100;
  const needleTip = polarToCartesian(cx, cy, r - 16, needleAngle);
  const { text, color } = riskLabel(score);

  const bandStops = [
    { from: 0, to: 40, color: 'var(--risk-low)' },
    { from: 40, to: 70, color: 'var(--risk-med)' },
    { from: 70, to: 100, color: 'var(--risk-high)' }
  ];

  return (
    <div className="gauge-wrap">
      <svg viewBox="0 0 200 190" className="gauge-svg" role="img" aria-label={`Overall risk score ${score} out of 100, ${text}`}>
        <circle cx={cx} cy={cy} r={92} className="gauge-ring" />
        {bandStops.map((b) => (
          <path
            key={b.from}
            d={arcPath(cx, cy, r, START_ANGLE + (SWEEP * b.from) / 100, START_ANGLE + (SWEEP * b.to) / 100)}
            fill="none"
            stroke={b.color}
            strokeWidth="10"
            strokeLinecap="butt"
            opacity="0.85"
          />
        ))}
        <line
          x1={cx}
          y1={cy}
          x2={needleTip.x}
          y2={needleTip.y}
          stroke="var(--ink)"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <circle cx={cx} cy={cy} r="5" fill="var(--ink)" />
        <text x={cx} y={cy + 40} textAnchor="middle" className="gauge-score">{score}</text>
        <text x={cx} y={cy + 58} textAnchor="middle" className="gauge-max">/ 100</text>
      </svg>
      <div className="gauge-verdict" style={{ color }}>{text}</div>
    </div>
  );
}
