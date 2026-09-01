import { useEffect, useRef, useState } from 'react';

const START_ANGLE = -210; // degrees, 0° = pointing right
const SWEEP       = 240;

function polar(cx, cy, r, deg) {
  const rad = (deg * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function arc(cx, cy, r, startDeg, endDeg) {
  if (Math.abs(endDeg - startDeg) < 0.01) return '';
  const s = polar(cx, cy, r, startDeg);
  const e = polar(cx, cy, r, endDeg);
  const large = endDeg - startDeg > 180 ? 1 : 0;
  return `M ${s.x} ${s.y} A ${r} ${r} 0 ${large} 1 ${e.x} ${e.y}`;
}

const BANDS = [
  { from: 0,  to: 40,  color: 'var(--risk-low)',  glow: 'var(--risk-low-glow)' },
  { from: 40, to: 70,  color: 'var(--risk-med)',  glow: 'var(--risk-med-glow)' },
  { from: 70, to: 100, color: 'var(--risk-high)', glow: 'var(--risk-high-glow)' },
];

function riskLabel(score) {
  if (score >= 70) return { text: 'High Risk',    cls: 'high', color: 'var(--risk-high)' };
  if (score >= 40) return { text: 'Medium Risk',  cls: 'med',  color: 'var(--risk-med)' };
  return               { text: 'Low Risk',        cls: 'low',  color: 'var(--risk-low)' };
}

export default function RiskGauge({ score = 0 }) {
  const cx = 110, cy = 110, r = 80;

  // Animate score counting up
  const [displayScore, setDisplayScore] = useState(0);
  const frameRef = useRef(null);

  useEffect(() => {
    const duration  = 1200; // ms
    const start     = performance.now();
    const startVal  = 0;

    function step(now) {
      const t = Math.min((now - start) / duration, 1);
      // ease-out cubic
      const eased = 1 - Math.pow(1 - t, 3);
      setDisplayScore(Math.round(startVal + eased * (score - startVal)));
      if (t < 1) frameRef.current = requestAnimationFrame(step);
    }
    frameRef.current = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frameRef.current);
  }, [score]);

  const needleAngle   = START_ANGLE + (SWEEP * displayScore) / 100;
  const needleTip     = polar(cx, cy, r - 14, needleAngle);
  const needleBase1   = polar(cx, cy, 8, needleAngle + 90);
  const needleBase2   = polar(cx, cy, 8, needleAngle - 90);
  const { text, cls, color } = riskLabel(score);

  // Active band for glow
  const activeBand = BANDS.find(b => score > b.from && score <= b.to) ?? BANDS[2];

  return (
    <div className="gauge-container">
      <svg
        viewBox="0 0 220 190"
        className="gauge-svg"
        role="img"
        aria-label={`Overall risk score ${score} out of 100: ${text}`}
      >
        <defs>
          <filter id="needle-glow">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
          <filter id="band-glow">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>

        {/* Track */}
        <path
          d={arc(cx, cy, r, START_ANGLE, START_ANGLE + SWEEP)}
          className="gauge-track"
          strokeWidth="12"
          fill="none"
        />

        {/* Colored bands */}
        {BANDS.map(b => (
          <path
            key={b.from}
            d={arc(cx, cy, r, START_ANGLE + (SWEEP * b.from) / 100, START_ANGLE + (SWEEP * b.to) / 100)}
            fill="none"
            stroke={b.color}
            strokeWidth="12"
            strokeLinecap="butt"
            opacity="0.7"
            filter={score > b.from && score <= b.to ? 'url(#band-glow)' : undefined}
          />
        ))}

        {/* Needle */}
        <polygon
          points={`${needleTip.x},${needleTip.y} ${needleBase1.x},${needleBase1.y} ${needleBase2.x},${needleBase2.y}`}
          fill={color}
          opacity="0.95"
          filter="url(#needle-glow)"
          className="gauge-needle"
        />
        {/* Needle hub */}
        <circle cx={cx} cy={cy} r="6" fill={color} opacity="0.9" />
        <circle cx={cx} cy={cy} r="3" fill="var(--bg-card)" />

        {/* Score display */}
        <text x={cx} y={cy + 34} textAnchor="middle" className="gauge-score-num"
          style={{ fontFamily: 'var(--font-display)', fontSize: '44px', fill: 'var(--text-primary)' }}>
          {displayScore}
        </text>
        <text x={cx} y={cy + 52} textAnchor="middle" className="gauge-score-denom"
          style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', fill: 'var(--text-muted)' }}>
          / 100
        </text>
      </svg>

      <div className={`gauge-verdict ${cls}`}>{text}</div>
    </div>
  );
}
