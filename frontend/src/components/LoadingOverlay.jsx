import { useState, useEffect } from 'react';

const STEPS = [
  'Parsing document…',
  'Extracting text & cleaning…',
  'Running Named Entity Recognition…',
  'Classifying legal clauses…',
  'Scoring risk levels…',
  'Generating analysis report…',
];

export default function LoadingOverlay() {
  const [stepIndex, setStepIndex] = useState(0);

  useEffect(() => {
    if (stepIndex >= STEPS.length - 1) return;
    const timer = setInterval(() => {
      setStepIndex(i => Math.min(i + 1, STEPS.length - 1));
    }, 700);
    return () => clearInterval(timer);
  }, [stepIndex]);

  return (
    <div className="loading-overlay" role="status" aria-label="Analyzing contract">
      <div className="loading-seal" aria-hidden="true" />

      <div>
        <div className="loading-text">Analyzing your contract</div>
        <div className="loading-sub">Powered by RoBERTa · spaCy · Gemini</div>
      </div>

      <div className="loading-steps">
        {STEPS.map((step, i) => (
          <div
            key={step}
            className={`loading-step ${i < stepIndex ? 'done' : i === stepIndex ? 'active' : ''}`}
          >
            <div className="step-dot" />
            <span>{i < stepIndex ? '✓ ' : ''}{step}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
