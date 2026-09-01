import { useState, useCallback } from 'react';
import LandingView from './components/LandingView.jsx';
import AnalysisDashboard from './components/AnalysisDashboard.jsx';
import LoadingOverlay from './components/LoadingOverlay.jsx';
import { analyzeContract } from './api/client.js';

export default function App() {
  const [view, setView]           = useState('landing');   // 'landing' | 'dashboard'
  const [file, setFile]           = useState(null);
  const [analysis, setAnalysis]   = useState(null);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState(null);

  const handleUpload = useCallback(async (selectedFile) => {
    if (!selectedFile) return;
    setFile(selectedFile);
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeContract(selectedFile);
      setAnalysis(result);
      setView('dashboard');
    } catch (err) {
      setError(err.message || 'Something went wrong analyzing this contract.');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleNewAnalysis = useCallback(() => {
    setView('landing');
    setFile(null);
    setAnalysis(null);
    setError(null);
  }, []);

  return (
    <>
      {loading && <LoadingOverlay />}

      {view === 'landing' && (
        <LandingView onUpload={handleUpload} error={error} />
      )}

      {view === 'dashboard' && analysis && (
        <AnalysisDashboard
          analysis={analysis}
          file={file}
          onNewAnalysis={handleNewAnalysis}
        />
      )}
    </>
  );
}
