import { useEffect, useRef, useState } from 'react';
import confetti from 'canvas-confetti';
import { ShieldCheck, ShieldAlert, AlertTriangle, Sparkles } from 'lucide-react';
import Card3D from './Card3D.jsx';

const START_ANGLE = -215;
const SWEEP = 250;

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

function getRiskMeta(score) {
  if (score >= 70) {
    return {
      text: 'HIGH RISK',
      subtext: 'Critical clauses require immediate review',
      cls: 'high',
      color: '#ff4d4d',
      glow: 'rgba(255, 77, 77, 0.45)',
      gradient: ['#ff4d4d', '#ff1a75'],
      Icon: ShieldAlert,
    };
  }
  if (score >= 40) {
    return {
      text: 'MODERATE RISK',
      subtext: 'Several clauses contain discretionary terms',
      cls: 'med',
      color: '#ffa600',
      glow: 'rgba(255, 166, 0, 0.40)',
      gradient: ['#ffa600', '#ff7700'],
      Icon: AlertTriangle,
    };
  }
  return {
    text: 'LOW RISK',
    subtext: 'Standard commercial terms with low exposure',
    cls: 'low',
    color: '#00e699',
    glow: 'rgba(0, 230, 153, 0.40)',
    gradient: ['#00e699', '#00b386'],
    Icon: ShieldCheck,
  };
}

export default function RiskGauge({ score = 0 }) {
  const cx = 130;
  const cy = 125;
  const r = 90;

  const [displayScore, setDisplayScore] = useState(0);
  const frameRef = useRef(null);

  useEffect(() => {
    const duration = 1400;
    const start = performance.now();

    function step(now) {
      const t = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - t, 4); // Quartic ease-out
      setDisplayScore(Math.round(eased * score));
      if (t < 1) frameRef.current = requestAnimationFrame(step);
    }
    frameRef.current = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frameRef.current);
  }, [score]);

  const meta = getRiskMeta(score);
  const progressDeg = START_ANGLE + (SWEEP * Math.min(Math.max(displayScore, 0), 100)) / 100;
  const needleTip = polar(cx, cy, r - 10, progressDeg);
  const needleP1 = polar(cx, cy, 10, progressDeg + 90);
  const needleP2 = polar(cx, cy, 10, progressDeg - 90);

  const handleCelebrate = () => {
    if (score < 40) {
      confetti({
        particleCount: 70,
        spread: 60,
        origin: { y: 0.7 },
        colors: ['#00e699', '#38bdf8', '#d4a843'],
      });
    }
  };

  return (
    <Card3D
      className="gauge-3d-card"
      maxTilt={6}
      scale={1.01}
      onClick={handleCelebrate}
      style={{
        cursor: 'pointer',
        boxShadow: `0 20px 50px rgba(0, 0, 0, 0.6), 0 0 35px ${meta.glow}`,
      }}
    >
      <div className="gauge-3d-header">
        <div className="gauge-status-badge" style={{ borderColor: meta.color, color: meta.color }}>
          <meta.Icon size={14} />
          <span>RISK RADAR HUD</span>
        </div>
        <div className="gauge-live-indicator">
          <span className="live-dot" style={{ background: meta.color, boxShadow: `0 0 8px ${meta.color}` }} />
          <span>REAL-TIME NLP</span>
        </div>
      </div>

      <div className="gauge-interactive-stage">
        <svg
          viewBox="0 0 260 215"
          className="gauge-svg-3d"
          role="img"
          aria-label={`Overall risk score ${score} out of 100: ${meta.text}`}
        >
          <defs>
            <linearGradient id="trackGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#00e699" />
              <stop offset="50%" stopColor="#ffa600" />
              <stop offset="100%" stopColor="#ff4d4d" />
            </linearGradient>

            <linearGradient id="activeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor={meta.gradient[0]} />
              <stop offset="100%" stopColor={meta.gradient[1]} />
            </linearGradient>

            <filter id="neonGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="4" result="blur1" />
              <feGaussianBlur stdDeviation="8" result="blur2" />
              <feMerge>
                <feMergeNode in="blur2" />
                <feMergeNode in="blur1" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>

            <radialGradient id="hubRadial" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor={meta.color} stopOpacity="0.8" />
              <stop offset="60%" stopColor="rgba(15, 23, 42, 0.9)" />
              <stop offset="100%" stopColor="#0a0e17" />
            </radialGradient>
          </defs>

          {/* Outer Bezel Tech Ring */}
          <circle
            cx={cx}
            cy={cy}
            r={r + 18}
            fill="none"
            stroke="rgba(255, 255, 255, 0.05)"
            strokeWidth="2"
            strokeDasharray="4 8"
          />

          {/* Background Track Arc */}
          <path
            d={arc(cx, cy, r, START_ANGLE, START_ANGLE + SWEEP)}
            fill="none"
            stroke="rgba(255, 255, 255, 0.08)"
            strokeWidth="14"
            strokeLinecap="round"
          />

          {/* Ambient Multi-spectrum Underlay */}
          <path
            d={arc(cx, cy, r, START_ANGLE, START_ANGLE + SWEEP)}
            fill="none"
            stroke="url(#trackGrad)"
            strokeWidth="3"
            strokeOpacity="0.35"
            strokeLinecap="round"
          />

          {/* Active Dynamic Progress Arc */}
          {displayScore > 0 && (
            <path
              d={arc(cx, cy, r, START_ANGLE, progressDeg)}
              fill="none"
              stroke="url(#activeGrad)"
              strokeWidth="14"
              strokeLinecap="round"
              filter="url(#neonGlow)"
            />
          )}

          {/* Center Holographic Core Ring */}
          <circle
            cx={cx}
            cy={cy}
            r="44"
            fill="url(#hubRadial)"
            stroke="rgba(255, 255, 255, 0.12)"
            strokeWidth="1.5"
          />
          <circle
            cx={cx}
            cy={cy}
            r="38"
            fill="none"
            stroke={meta.color}
            strokeWidth="1"
            strokeOpacity="0.4"
            strokeDasharray="6 4"
            className="pulse-spin"
          />

          {/* Needle Indicator */}
          <polygon
            points={`${needleTip.x},${needleTip.y} ${needleP1.x},${needleP1.y} ${needleP2.x},${needleP2.y}`}
            fill={meta.color}
            filter="url(#neonGlow)"
            opacity="0.95"
          />

          {/* Central Score HUD Typography */}
          <text
            x={cx}
            y={cy + 6}
            textAnchor="middle"
            className="gauge-hud-score"
            style={{ fill: '#ffffff', filter: 'drop-shadow(0 0 10px rgba(255,255,255,0.4))' }}
          >
            {displayScore}
          </text>
          <text
            x={cx}
            y={cy + 22}
            textAnchor="middle"
            className="gauge-hud-sub"
            style={{ fill: 'var(--text-muted)' }}
          >
            / 100
          </text>
        </svg>

        {/* Verdict Badge */}
        <div
          className="gauge-verdict-banner"
          style={{
            background: `linear-gradient(135deg, ${meta.color}18, rgba(13, 17, 23, 0.8))`,
            borderColor: `${meta.color}44`,
          }}
        >
          <div className="verdict-title" style={{ color: meta.color }}>
            {meta.text}
          </div>
          <div className="verdict-subtext">{meta.subtext}</div>
        </div>
      </div>
    </Card3D>
  );
}
