import React from 'react';

interface RunningPlanProps {
  plan: {
    id: string;
    name: string;
    progress: number;
    status: string;
  } | null;
  monitorMode?: boolean;
}

const RunningPlan: React.FC<RunningPlanProps> = ({ plan, monitorMode = false }) => {
  return (
    <div className="section">
      <h2>Running Plan</h2>
      <div className="plan-display">
        {plan ? (
          <div>
            <h3>{plan.name}</h3>
            <p>Status: {plan.status}</p>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${plan.progress}%` }}
              ></div>
            </div>
            <p>{plan.progress}% complete</p>
            {!monitorMode && (
              <div>
                <button>Stop</button>
                <button>Pause</button>
              </div>
            )}
          </div>
        ) : (
          <p>No plan currently running</p>
        )}
      </div>
    </div>
  );
};

export default RunningPlan;