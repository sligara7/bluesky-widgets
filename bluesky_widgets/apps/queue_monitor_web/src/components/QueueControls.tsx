import React from 'react';

interface QueueControlsProps {
  onAddPlan: () => void;
  onClearQueue: () => void;
}

const QueueControls: React.FC<QueueControlsProps> = ({ onAddPlan, onClearQueue }) => {
  return (
    <div className="section">
      <h2>Queue Controls</h2>
      <div className="control-buttons">
        <button onClick={onAddPlan}>Add Plan</button>
        <button onClick={onClearQueue}>Clear Queue</button>
      </div>
    </div>
  );
};

export default QueueControls;