import { useState } from 'react';
import DashboardHeader from './DashboardHeader.jsx';
import ContractViewer from './ContractViewer.jsx';
import RiskGauge from './RiskGauge.jsx';
import ClauseCard from './ClauseCard.jsx';
import EntitiesPanel from './EntitiesPanel.jsx';
import QAChat from './QAChat.jsx';

const TABS = [
  { id: 'overview',  label: 'Overview',  icon: '📊' },
  { id: 'contract',  label: 'Contract',  icon: '📄' },
  { id: 'entities',  label: 'Entities',  icon: '🏷️' },
  { id: 'ask',       label: 'Ask AI',    icon: '💬' },
];

export default function AnalysisDashboard({ analysis, file, onNewAnalysis }) {
  const [activeTab, setActiveTab]           = useState('overview');
  const [selectedClauseId, setSelectedClauseId] = useState(null);

  const { overallRisk, clauses, entities, filename, fullText } = analysis;

  const highRisk   = clauses.filter(c => c.risk === 'high').length;
  const medRisk    = clauses.filter(c => c.risk === 'medium').length;
  const clauseTexts = clauses.map(c => c.text);

  function handleSelectClause(id) {
    setSelectedClauseId(id);
    // If we're on the overview tab, switch to contract for inline highlight
    if (activeTab === 'overview') setActiveTab('contract');
    // Scroll to clause mark in the contract viewer
    requestAnimationFrame(() => {
      const el = document.getElementById(`clause-${id}`);
      el?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  }

  return (
    <div className="dash-shell">
      <DashboardHeader
        filename={filename}
        file={file}
        overallRisk={overallRisk}
        onNewAnalysis={onNewAnalysis}
      />

      <div className="dash-body">
        {/* ── Left: Contract viewer with tabs ── */}
        <div className="viewer-pane">
          <div className="viewer-tabs-area">
            <div className="tab-bar" role="tablist">
              {TABS.map(tab => (
                <button
                  key={tab.id}
                  id={`tab-${tab.id}`}
                  role="tab"
                  aria-selected={activeTab === tab.id}
                  aria-controls={`tabpanel-${tab.id}`}
                  className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  <span className="tab-icon">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          <div
            id={`tabpanel-${activeTab}`}
            role="tabpanel"
            aria-labelledby={`tab-${activeTab}`}
            style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}
          >
            {activeTab === 'overview' && (
              <OverviewTab
                overallRisk={overallRisk}
                highRisk={highRisk}
                medRisk={medRisk}
                clauses={clauses}
                selectedClauseId={selectedClauseId}
                onSelectClause={handleSelectClause}
                rawTextLength={analysis.rawTextLength}
              />
            )}
            {activeTab === 'contract' && (
              <div className="viewer-scroll">
                <ContractViewer
                  fullText={fullText}
                  clauses={clauses}
                  filename={filename}
                  selectedClauseId={selectedClauseId}
                  onSelectClause={handleSelectClause}
                />
              </div>
            )}
            {activeTab === 'entities' && (
              <div className="viewer-scroll">
                <EntitiesPanel entities={entities} />
              </div>
            )}
            {activeTab === 'ask' && (
              <QAChat clauseTexts={clauseTexts} />
            )}
          </div>
        </div>

        {/* ── Right: Risk + Clauses sidebar ── */}
        <div className="side-pane">
          <div className="side-scroll">
            {/* Risk Gauge */}
            <div className="overview-section">
              <RiskGauge score={overallRisk} />
            </div>

            {/* Summary stats */}
            <div className="overview-section">
              <div className="section-title">Summary</div>
              <div className="stats-row">
                <div className="stat-card">
                  <div className="stat-value" style={{ color: 'var(--risk-high)' }}>{highRisk}</div>
                  <div className="stat-label">High Risk</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value" style={{ color: 'var(--risk-med)' }}>{medRisk}</div>
                  <div className="stat-label">Medium Risk</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{clauses.length}</div>
                  <div className="stat-label">Total Clauses</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{entities.length}</div>
                  <div className="stat-label">Entities Found</div>
                </div>
              </div>
            </div>

            {/* Clause list */}
            <div className="overview-section">
              <div className="section-title">Flagged Clauses ({clauses.length})</div>
              <ul className="clause-list" role="list">
                {[...clauses]
                  .sort((a, b) => b.riskScore - a.riskScore)
                  .map(clause => (
                    <ClauseCard
                      key={clause.id}
                      clause={clause}
                      isSelected={selectedClauseId === clause.id}
                      onSelect={handleSelectClause}
                    />
                  ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Overview Tab (full-width layout) ──────────────────────────────────────
function OverviewTab({ overallRisk, highRisk, medRisk, clauses, selectedClauseId, onSelectClause, rawTextLength }) {
  const chars = rawTextLength ? rawTextLength.toLocaleString() : '—';
  const verdict = overallRisk >= 70 ? '🔴 High Risk — Requires immediate legal review'
                : overallRisk >= 40 ? '🟡 Moderate Risk — Review flagged clauses carefully'
                : '🟢 Low Risk — Standard contract with minor concerns';

  return (
    <div className="viewer-scroll">
      {/* Verdict Banner */}
      <div
        style={{
          background: overallRisk >= 70 ? 'var(--risk-high-bg)' : overallRisk >= 40 ? 'var(--risk-med-bg)' : 'var(--risk-low-bg)',
          border: `1px solid ${overallRisk >= 70 ? 'var(--risk-high-border)' : overallRisk >= 40 ? 'var(--risk-med-border)' : 'var(--risk-low-border)'}`,
          borderRadius: 'var(--radius-md)',
          padding: '16px 20px',
          marginBottom: '28px',
          fontSize: '14px',
          color: 'var(--text-primary)',
          fontWeight: 500,
        }}
        role="alert"
      >
        {verdict}
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '28px' }}>
        {[
          { label: 'Risk Score',    value: `${overallRisk}/100`, color: overallRisk >= 70 ? 'var(--risk-high)' : overallRisk >= 40 ? 'var(--risk-med)' : 'var(--risk-low)' },
          { label: 'High-Risk Clauses', value: highRisk, color: 'var(--risk-high)' },
          { label: 'Total Clauses', value: clauses.length, color: 'var(--text-primary)' },
          { label: 'Document Size', value: `${chars} chars`, color: 'var(--text-secondary)', small: true },
        ].map(stat => (
          <div key={stat.label} className="stat-card">
            <div className="stat-value" style={{ color: stat.color, fontSize: stat.small ? '20px' : undefined }}>
              {stat.value}
            </div>
            <div className="stat-label">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Clause list preview */}
      <div className="section-title" style={{ marginBottom: '12px' }}>All Clauses</div>
      <ul className="clause-list" role="list">
        {[...clauses]
          .sort((a, b) => b.riskScore - a.riskScore)
          .map(clause => (
            <ClauseCard
              key={clause.id}
              clause={clause}
              isSelected={selectedClauseId === clause.id}
              onSelect={onSelectClause}
            />
          ))}
      </ul>
    </div>
  );
}
