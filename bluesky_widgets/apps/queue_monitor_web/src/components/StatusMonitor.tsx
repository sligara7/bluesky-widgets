import React from 'react';

interface StatusMonitorProps {
  status: string;
}

const StatusMonitor: React.FC<StatusMonitorProps> = ({ status }) => {
  return (
    <div className="status-section">
      <h2>Status Monitor</h2>
      <div className="status-info">
        <p>Status: {status}</p>
      </div>
    </div>
  );
};

export default StatusMonitor;