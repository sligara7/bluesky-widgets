import React from 'react';

interface ConsoleMonitorProps {
  logs: string[];
}

const ConsoleMonitor: React.FC<ConsoleMonitorProps> = ({ logs }) => {
  return (
    <div className="section">
      <h2>Console Monitor</h2>
      <div className="console-display">
        {logs.length === 0 ? (
          <p>No console output</p>
        ) : (
          <pre>
            {logs.map((log, index) => (
              <div key={index}>{log}</div>
            ))}
          </pre>
        )}
      </div>
    </div>
  );
};

export default ConsoleMonitor;