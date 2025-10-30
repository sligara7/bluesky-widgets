import React from 'react';

interface Plan {
  id: string;
  name: string;
  status: string;
}

interface PlanQueueProps {
  plans: Plan[];
  monitorMode?: boolean;
  onRemove?: (id: string) => void;
}

const PlanQueue: React.FC<PlanQueueProps> = ({ plans, monitorMode = false, onRemove }) => {
  return (
    <div className="section">
      <h2>Plan Queue</h2>
      <div className="queue-display">
        {plans.length === 0 ? (
          <p>Queue is empty</p>
        ) : (
          <ul>
            {plans.map((plan) => (
              <li key={plan.id}>
                <strong>{plan.name}</strong> - {plan.status}
                {!monitorMode && (
                  <div>
                    <button>Edit</button>
                    <button onClick={() => onRemove && onRemove(plan.id)}>Remove</button>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default PlanQueue;