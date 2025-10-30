import React from 'react';

interface ExecutionControlsProps {
  isRunning: boolean;
  onStart: () => void;
  onStop: () => void;
  envOpen?: boolean;
}

const ExecutionControls: React.FC<ExecutionControlsProps> = ({
  isRunning,
  onStart,
  onStop,
  envOpen = false
}) => {
  return (
    <div className="section">
      <h2>Execution Controls</h2>
      <div className="control-buttons">
        <button onClick={onStart} disabled={isRunning || !envOpen}>Start Queue</button>
        <button onClick={onStop} disabled={!isRunning}>Stop Queue</button>
      </div>
    </div>
  );
};

export default ExecutionControls;