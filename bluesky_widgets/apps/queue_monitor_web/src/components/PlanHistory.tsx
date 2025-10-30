import React, { useState, useCallback } from 'react';
import RunViewer from './RunViewer';
import useSSE from '../hooks/useSSE';

interface HistoryItem {
  id: string;
  name: string;
  completedAt: string;
  success: boolean;
}

interface PlanHistoryProps {
  history: HistoryItem[];
  onRerun?: (item: HistoryItem) => void;
}

const PlanHistory: React.FC<PlanHistoryProps> = ({ history, onRerun }) => {
  const [openRun, setOpenRun] = useState<string | null>(null);
  const [runDocs, setRunDocs] = useState<any[]>([]);

  const fetchRunDocs = useCallback(async (uid: string) => {
    try {
      const res = await fetch(`/runs/${uid}/documents`);
      if (res.ok) {
        const j = await res.json();
        setRunDocs(j.documents || []);
        setOpenRun(uid);
      }
    } catch (e) {
      console.error('Failed to fetch run documents', e);
    }
  }, []);

  // Subscribe to SSE and update run docs if the open run receives live docs
  useSSE('/events', (doc) => {
    if (!openRun) return;
    if (doc.get && typeof doc.get === 'function') {
      // unlikely; ignore
    }
    // if doc has uid and matches open run, append it
    if (doc.uid && doc.uid === openRun) {
      setRunDocs((prev) => [...prev, doc]);
    }
  });

  return (
    <div className="section">
      <h2>Plan History</h2>
      <div className="history-display">
        {history.length === 0 ? (
          <p>No plans in history</p>
        ) : (
          <ul>
            {history.map((item) => (
              <li key={item.id}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ flex: 1 }}>
                    <strong>{item.name}</strong> - {item.completedAt}
                    <span className={item.success ? 'success' : 'failure'}>
                      {item.success ? '✓' : '✗'}
                    </span>
                  </div>
                  <div>
                    <button onClick={() => onRerun && onRerun(item)}>Rerun</button>
                    <button onClick={() => fetchRunDocs(item.id)} style={{ marginLeft: 8 }}>
                      View Run
                    </button>
                  </div>
                </div>
                {openRun === item.id && <RunViewer uid={item.id} documents={runDocs} />}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default PlanHistory;