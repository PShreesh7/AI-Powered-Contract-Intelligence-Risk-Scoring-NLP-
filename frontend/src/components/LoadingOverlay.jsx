import { useState, useEffect } from 'react';
import { Scale, CheckCircle2, Loader2, Sparkles } from 'lucide-react';

const STEPS = [
  'Ingesting & parsing document bytes…',
  'Normalizing whitespace & splitting clauses…',
  'Running spaCy legal Named Entity Recognition…',
  'Executing zero-shot / fine-tuned clause classification…',
  'Evaluating multi-rule risk heuristics & suggestions…',
  'Synthesizing full intelligence report…',
];

export default function LoadingOverlay() {
  const [stepIndex, setStepIndex] = useState(0);

  useEffect(() => {
    if (stepIndex >= STEPS.length - 1) return;
    const timer = setInterval(() => {
      setStepIndex((i) => Math.min(i + 1, STEPS.length - 1));
    }, 700);
    return () => clearInterval(timer);
  }, [stepIndex]);

  return (
    <div className="loading-overlay-3d" role="status" aria-label="Analyzing contract">
      {/* 3D Holographic Scanner Seal */}
      <div className="hologram-loader-wrap">
        <div className="orbital-ring ring-1" />
        <div className="orbital-ring ring-2" />
        <div className="orbital-ring ring-3" />
        <div className="loader-core-icon">
          <Scale size={36} className="loader-scale" />
        </div>
      </div>

      <div className="loader-heading-wrap">
        <div className="loader-eyebrow">
          <Sparkles size={14} className="sparkle-icon" />
          <span>NEURAL PIPELINE ACTIVE</span>
        </div>
        <div className="loader-main-title">Deconstructing Contract Provisions</div>
        <div className="loader-sub">spaCy NER · Transformers · Risk Engine</div>
      </div>

      <div className="loader-stepper-box">
        {STEPS.map((step, i) => {
          const isDone = i < stepIndex;
          const isActive = i === stepIndex;
          return (
            <div
              key={step}
              className={`stepper-row ${isDone ? 'is-done' : ''} ${isActive ? 'is-active' : ''}`}
            >
              <div className="stepper-indicator">
                {isDone ? (
                  <CheckCircle2 size={16} className="check-icon" />
                ) : isActive ? (
                  <Loader2 size={16} className="spin-icon" />
                ) : (
                  <div className="stepper-dot" />
                )}
              </div>
              <span className="stepper-label">{step}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
