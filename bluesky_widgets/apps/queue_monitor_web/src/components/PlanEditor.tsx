import React, { useState } from 'react';

interface PlanEditorProps {
  onSavePlan: (planCode: string) => void;
}

const PlanEditor: React.FC<PlanEditorProps> = ({ onSavePlan }) => {
  const [planCode, setPlanCode] = useState('');

  const handleSave = () => {
    onSavePlan(planCode);
  };

  return (
    <div className="section">
      <h2>Plan Editor</h2>
      <textarea
        value={planCode}
        onChange={(e) => setPlanCode(e.target.value)}
        placeholder="Enter plan code here..."
        rows={15}
      />
      <div className="editor-buttons">
        <button onClick={handleSave}>Save Plan</button>
        <button onClick={() => setPlanCode('')}>Clear</button>
      </div>
    </div>
  );
};

export default PlanEditor;