import React from 'react';

interface EnvironmentControlsProps {
  envDestroyActivated: boolean;
  envOpen?: boolean;
  onToggleEnvDestroy: () => void;
  onOpenEnvironment?: () => void;
  onCloseEnvironment?: () => void;
}

const EnvironmentControls: React.FC<EnvironmentControlsProps> = ({
  envDestroyActivated,
  envOpen = false,
  onToggleEnvDestroy,
  onOpenEnvironment,
  onCloseEnvironment
}) => {
  return (
    <div className="section">
      <h2>Environment Controls</h2>
      <div className="control-buttons">
        <button onClick={onOpenEnvironment} disabled={envOpen}>Open Environment</button>
        <button onClick={onCloseEnvironment} disabled={!envOpen}>Close Environment</button>
      </div>
      <div style={{ marginTop: 10 }}>
        <button onClick={onToggleEnvDestroy}>
          {envDestroyActivated ? 'Deactivate' : 'Activate'} Environment Destroy
        </button>
      </div>
    </div>
  );
};

export default EnvironmentControls;