import { useState, useMemo } from 'react';
import {
  LayoutDashboard,
  FileText,
  Tags,
  MessageSquareCode,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  FileCode,
  Layers,
  Search,
  Filter,
  Sparkles,
} from 'lucide-react';
import DashboardHeader from './DashboardHeader.jsx';
import ContractViewer from './ContractViewer.jsx';
import RiskGauge from './RiskGauge.jsx';
import ClauseCard from './ClauseCard.jsx';
import EntitiesPanel from './EntitiesPanel.jsx';
import QAChat from './QAChat.jsx';
import Card3D from './Card3D.jsx';

const TABS = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'contract', label: 'Contract Text', icon: FileText },
  { id: 'entities', label: 'Entities', icon: Tags },
  { id: 'ask', label: 'Ask AI Chat', icon: MessageSquareCode },
];

export default function AnalysisDashboard({ analysis, file, onNewAnalysis }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedClauseId, setSelectedClauseId] = useState(null);

  const { overallRisk, clauses = [], entities = [], filename, fullText } = analysis;

  const highRisk = clauses.filter((c) => c.risk === 'high').length;
  const medRisk = clauses.filter((c) => c.risk === 'medium').length;
  const lowRisk = clauses.filter((c) => c.risk === 'low').length;
  const clauseTexts = useMemo(() => clauses.map((c) => c.text), [clauses]);

  function handleSelectClause(id) {
    setSelectedClauseId(id);
    if (activeTab === 'overview') setActiveTab('contract');
    requestAnimationFrame(() => {
      const el = document.getElementById(`clause-${id}`);
      el?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  }

  return (
    <div className="dash-shell-3d">
      <DashboardHeader
        filename={filename}
        file={file}
        overallRisk={overallRisk}
        onNewAnalysis={onNewAnalysis}
      />

      <div className="dash-main-layout">
        {/* ── Center Content Area with Tabs ── */}
        <div className="content-pane-3d">
          <div className="tab-control-bar">
            <div className="tab-pills-wrap" role="tablist">
              {TABS.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    id={`tab-${tab.id}`}
                    role="tab"
                    aria-selected={isActive}
                    className={`nav-tab-btn ${isActive ? 'is-active' : ''}`}
                    onClick={() => setActiveTab(tab.id)}
                  >
                    <Icon size={16} />
                    <span>{tab.label}</span>
                    {tab.id === 'ask' && <span className="ai-badge">Gemini</span>}
                  </button>
                );
              })}
            </div>
          </div>

          <div
            id={`tabpanel-${activeTab}`}
            role="tabpanel"
            className="tab-content-area"
          >
            {activeTab === 'overview' && (
              <OverviewTab
                overallRisk={overallRisk}
                highRisk={highRisk}
                medRisk={medRisk}
                lowRisk={lowRisk}
                clauses={clauses}
                selectedClauseId={selectedClauseId}
                onSelectClause={handleSelectClause}
                rawTextLength={analysis.rawTextLength}
                entitiesCount={entities.length}
              />
            )}
            {activeTab === 'contract' && (
              <div className="tab-scroll-container">
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
              <div className="tab-scroll-container">
                <EntitiesPanel entities={entities} />
              </div>
            )}
            {activeTab === 'ask' && <QAChat clauseTexts={clauseTexts} />}
          </div>
        </div>

        {/* ── Right Sidebar: Radar & Flagged clauses ── */}
        <aside className="sidebar-pane-3d">
          <div className="sidebar-scroll">
            <div className="sidebar-block">
              <RiskGauge score={overallRisk} />
            </div>

            {/* Quick Metrics */}
            <div className="sidebar-block">
              <div className="sidebar-heading">
                <Layers size={15} />
                <span>CONTRACT COMPOSITION</span>
              </div>
              <div className="mini-stats-grid">
                <Card3D className="mini-stat-box" maxTilt={6}>
                  <div className="mini-stat-num text-danger">{highRisk}</div>
                  <div className="mini-stat-lbl">High Risk</div>
                </Card3D>
                <Card3D className="mini-stat-box" maxTilt={6}>
                  <div className="mini-stat-num text-warning">{medRisk}</div>
                  <div className="mini-stat-lbl">Medium Risk</div>
                </Card3D>
                <Card3D className="mini-stat-box" maxTilt={6}>
                  <div className="mini-stat-num text-success">{lowRisk}</div>
                  <div className="mini-stat-lbl">Low Risk</div>
                </Card3D>
                <Card3D className="mini-stat-box" maxTilt={6}>
                  <div className="mini-stat-num text-accent">{entities.length}</div>
                  <div className="mini-stat-lbl">Entities</div>
                </Card3D>
              </div>
            </div>

            {/* Ranked Clauses */}
            <div className="sidebar-block">
              <div className="sidebar-heading">
                <ShieldAlert size={15} />
                <span>PRIORITY REVIEW QUEUE ({clauses.length})</span>
              </div>
              <ul className="sidebar-clause-list">
                {[...clauses]
                  .sort((a, b) => b.riskScore - a.riskScore)
                  .map((clause) => (
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
        </aside>
      </div>
    </div>
  );
}

// ── Overview Tab Component ──────────────────────────────────────────────────
function OverviewTab({
  overallRisk,
  highRisk,
  medRisk,
  lowRisk,
  clauses,
  selectedClauseId,
  onSelectClause,
  rawTextLength,
  entitiesCount,
}) {
  const [filterRisk, setFilterRisk] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  const chars = rawTextLength ? rawTextLength.toLocaleString() : '—';

  const verdict =
    overallRisk >= 70
      ? {
          title: 'High Legal Risk Detected',
          desc: 'Critical exposure identified in indemnification, liability, or termination rights. Immediate counsel renegotiation strongly advised.',
          cls: 'danger',
          color: '#ff4d4d',
        }
      : overallRisk >= 40
      ? {
          title: 'Moderate Contract Exposure',
          desc: 'Document contains one-sided discretionary powers or open-ended renewal commitments. Review flagged clauses before signing.',
          cls: 'warning',
          color: '#ffa600',
        }
      : {
          title: 'Standard Commercial Terms',
          desc: 'Favorable provisions with customary liability caps and bilateral termination terms. Low legal risk profile.',
          cls: 'success',
          color: '#00e699',
        };

  const filteredClauses = useMemo(() => {
    return clauses.filter((c) => {
      const matchesFilter = filterRisk === 'all' || c.risk === filterRisk;
      const matchesSearch =
        !searchQuery.trim() ||
        c.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.text.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.clauseType.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesFilter && matchesSearch;
    });
  }, [clauses, filterRisk, searchQuery]);

  return (
    <div className="tab-scroll-container">
      {/* 3D Cinematic Verdict HUD */}
      <Card3D
        className={`verdict-hud-card hud-${verdict.cls}`}
        maxTilt={4}
        scale={1.01}
      >
        <div className="verdict-hud-left">
          <div className="verdict-beacon">
            <div className="beacon-ring" style={{ borderColor: verdict.color }} />
            <div className="beacon-core" style={{ background: verdict.color }} />
          </div>
          <div>
            <div className="verdict-status-title" style={{ color: verdict.color }}>
              {verdict.title}
            </div>
            <p className="verdict-status-desc">{verdict.desc}</p>
          </div>
        </div>

        <div className="verdict-hud-stats">
          <div className="hud-metric">
            <span className="metric-label">SCORE</span>
            <span className="metric-val" style={{ color: verdict.color }}>
              {overallRisk}
            </span>
          </div>
          <div className="hud-metric-sep" />
          <div className="hud-metric">
            <span className="metric-label">FLAGGED</span>
            <span className="metric-val text-danger">{highRisk + medRisk}</span>
          </div>
        </div>
      </Card3D>

      {/* 4 Interactive 3D Stat Cards */}
      <div className="overview-stats-3d">
        <Card3D className="stat-card-3d" maxTilt={8}>
          <div className="stat-icon-wrap text-accent">
            <Sparkles size={20} />
          </div>
          <div className="stat-metric-val">{overallRisk}<span className="stat-unit">/100</span></div>
          <div className="stat-metric-lbl">Overall Risk Index</div>
          <div className="stat-bar-track">
            <div
              className="stat-bar-fill"
              style={{
                width: `${overallRisk}%`,
                background: verdict.color,
                boxShadow: `0 0 10px ${verdict.color}`,
              }}
            />
          </div>
        </Card3D>

        <Card3D className="stat-card-3d" maxTilt={8}>
          <div className="stat-icon-wrap text-danger">
            <ShieldAlert size={20} />
          </div>
          <div className="stat-metric-val text-danger">{highRisk}</div>
          <div className="stat-metric-lbl">High-Risk Clauses</div>
          <div className="stat-bar-track">
            <div
              className="stat-bar-fill"
              style={{
                width: `${clauses.length ? (highRisk / clauses.length) * 100 : 0}%`,
                background: '#ff4d4d',
                boxShadow: '0 0 10px #ff4d4d',
              }}
            />
          </div>
        </Card3D>

        <Card3D className="stat-card-3d" maxTilt={8}>
          <div className="stat-icon-wrap text-success">
            <FileCode size={20} />
          </div>
          <div className="stat-metric-val">{clauses.length}</div>
          <div className="stat-metric-lbl">Total Clauses Segmented</div>
          <div className="stat-bar-track">
            <div
              className="stat-bar-fill"
              style={{ width: '100%', background: '#00e699', boxShadow: '0 0 10px #00e699' }}
            />
          </div>
        </Card3D>

        <Card3D className="stat-card-3d" maxTilt={8}>
          <div className="stat-icon-wrap text-primary">
            <FileText size={20} />
          </div>
          <div className="stat-metric-val">{chars}</div>
          <div className="stat-metric-lbl">Document Characters</div>
          <div className="stat-bar-track">
            <div
              className="stat-bar-fill"
              style={{ width: '85%', background: '#38bdf8', boxShadow: '0 0 10px #38bdf8' }}
            />
          </div>
        </Card3D>
      </div>

      {/* Filter and Clause Section */}
      <div className="clause-stream-section">
        <div className="clause-stream-header">
          <div className="stream-title-wrap">
            <div className="stream-heading">ANALYZED CLAUSES</div>
            <div className="stream-count-badge">{filteredClauses.length} OF {clauses.length}</div>
          </div>

          <div className="stream-controls">
            {/* Search Input */}
            <div className="stream-search-box">
              <Search size={14} className="search-icon" />
              <input
                type="text"
                placeholder="Search clauses or terms…"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            {/* Risk Filters */}
            <div className="stream-filters">
              {['all', 'high', 'medium', 'low'].map((filterKey) => (
                <button
                  key={filterKey}
                  type="button"
                  className={`filter-chip ${filterRisk === filterKey ? 'active' : ''} chip-${filterKey}`}
                  onClick={() => setFilterRisk(filterKey)}
                >
                  {filterKey.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Clause Cards Stream */}
        {filteredClauses.length === 0 ? (
          <div className="empty-stream-card">
            <AlertTriangle size={24} className="empty-icon" />
            <p>No clauses match the selected search or risk filter.</p>
          </div>
        ) : (
          <div className="clause-grid-stream">
            {filteredClauses.map((clause) => (
              <ClauseCard
                key={clause.id}
                clause={clause}
                isSelected={selectedClauseId === clause.id}
                onSelect={onSelectClause}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
