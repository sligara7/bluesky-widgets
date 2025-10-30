import React, { useState } from 'react';
import './App.css';
import {
  Connection,
  StatusMonitor,
  PlanQueue,
  RunningPlan,
  PlanHistory,
  ConsoleMonitor,
  EnvironmentControls,
  QueueControls,
  ExecutionControls,
  PlanEditor
} from './components';

interface Plan {
  id: string;
  name: string;
  status: string;
}

interface HistoryItem {
  id: string;
  name: string;
  completedAt: string;
  success: boolean;
}

function App() {
  // Render both Monitor and Edit sections on a single page
  const [isConnected, setIsConnected] = useState(false);
  const [status, setStatus] = useState('Unknown');
  const [plans, setPlans] = useState<Plan[]>([]);
  const [runningPlan, setRunningPlan] = useState<{
    id: string;
    name: string;
    progress: number;
    status: string;
  } | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [envDestroyActivated, setEnvDestroyActivated] = useState(false);
  const [envOpen, setEnvOpen] = useState(false);
  const [isRunning, setIsRunning] = useState(false);

  const handleConnect = () => {
    setIsConnected(true);
    setStatus('Connected');
    setLogs(prev => [...prev, 'Connected to queue server']);
  };

  const handleDisconnect = () => {
    setIsConnected(false);
    setStatus('Disconnected');
    setLogs(prev => [...prev, 'Disconnected from queue server']);
  };

  const handleToggleEnvDestroy = () => {
    setEnvDestroyActivated(!envDestroyActivated);
  };

  const handleOpenEnvironment = () => {
    setEnvOpen(true);
    setLogs((prev) => [...prev, 'Environment opened']);
  };

  const handleCloseEnvironment = () => {
    setEnvOpen(false);
    setLogs((prev) => [...prev, 'Environment closed']);
  };

  const handleAddPlan = () => {
    const newPlan: Plan = {
      id: Date.now().toString(),
      name: `Plan ${plans.length + 1}`,
      status: 'Queued'
    };
    setPlans(prev => [...prev, newPlan]);
  };

  const handleRemovePlan = (id: string) => {
    setPlans((prev) => prev.filter((p) => p.id !== id));
  };

  const handleRerunFromHistory = (item: HistoryItem) => {
    const newPlan: Plan = { id: Date.now().toString(), name: item.name, status: 'Queued' };
    setPlans((prev) => [...prev, newPlan]);
    setLogs((prev) => [...prev, `Requeued plan from history: ${item.name}`]);
  };

  const handleClearQueue = () => {
    setPlans([]);
  };

  const handleStartQueue = () => {
    if (!envOpen) {
      setLogs((prev) => [...prev, 'Cannot start: environment is closed']);
      return;
    }
    setIsRunning(true);
    if (plans.length > 0) {
      const plan = plans[0];
      setRunningPlan({ id: plan.id, name: plan.name, progress: 0, status: 'Running' });
      setPlans((prev) => prev.slice(1));
      setLogs((prev) => [...prev, `Started plan: ${plan.name}`]);
    }
  };

  const handleStopQueue = () => {
    setIsRunning(false);
    if (runningPlan) {
      setHistory(prev => [...prev, {
        id: runningPlan.id,
        name: runningPlan.name,
        completedAt: new Date().toLocaleString(),
        success: false
      }]);
      setRunningPlan(null);
    }
  };

  const handleSavePlan = (planCode: string) => {
    console.log('Saving plan:', planCode);
    // In a real implementation, this would send the plan to the server
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>BlueSky Queue Monitor</h1>
      </header>
      <div className="flow-layout">
        <div className="flow-column connection-col">
          <Connection isConnected={isConnected} onConnect={handleConnect} onDisconnect={handleDisconnect} />
          <QueueControls onAddPlan={handleAddPlan} onClearQueue={handleClearQueue} />
          <PlanEditor onSavePlan={handleSavePlan} />
          <PlanQueue plans={plans} onRemove={handleRemovePlan} />
        </div>

        <div className="flow-column env-col">
          <EnvironmentControls envOpen={envOpen} envDestroyActivated={envDestroyActivated} onOpenEnvironment={handleOpenEnvironment} onCloseEnvironment={handleCloseEnvironment} onToggleEnvDestroy={handleToggleEnvDestroy} />
        </div>

        <div className="flow-column exec-col">
          <ExecutionControls isRunning={isRunning} onStart={handleStartQueue} onStop={handleStopQueue} envOpen={envOpen} />
          <RunningPlan plan={runningPlan} />
        </div>

        <div className="flow-column history-col">
          <PlanHistory history={history} onRerun={handleRerunFromHistory} />
        </div>
      </div>

      <div className="console-bottom">
        <ConsoleMonitor logs={logs} />
      </div>
    </div>
  );
}

interface MonitorTabProps {
  isConnected: boolean;
  status: string;
  plans: Plan[];
  runningPlan: any;
  history: HistoryItem[];
  logs: string[];
  onConnect: () => void;
  onDisconnect: () => void;
}

function MonitorTab({
  isConnected,
  status,
  plans,
  runningPlan,
  history,
  logs,
  onConnect,
  onDisconnect
}: MonitorTabProps) {
  return (
    <div className="monitor-tab">
      <Connection
        isConnected={isConnected}
        onConnect={onConnect}
        onDisconnect={onDisconnect}
      />
      <StatusMonitor status={status} />
      <div className="queue-sections">
        <RunningPlan plan={runningPlan} monitorMode />
        <PlanQueue plans={plans} monitorMode />
        <PlanHistory history={history} />
        <ConsoleMonitor logs={logs} />
      </div>
    </div>
  );
}

interface EditTabProps {
  isConnected: boolean;
  status: string;
  plans: Plan[];
  runningPlan: any;
  history: HistoryItem[];
  envDestroyActivated: boolean;
  isRunning: boolean;
  onConnect: () => void;
  onDisconnect: () => void;
  onToggleEnvDestroy: () => void;
  onAddPlan: () => void;
  onClearQueue: () => void;
  onStart: () => void;
  onStop: () => void;
  onSavePlan: (planCode: string) => void;
}

function EditTab({
  isConnected,
  status,
  plans,
  runningPlan,
  history,
  envDestroyActivated,
  isRunning,
  onConnect,
  onDisconnect,
  onToggleEnvDestroy,
  onAddPlan,
  onClearQueue,
  onStart,
  onStop,
  onSavePlan
}: EditTabProps) {
  return (
    <div className="edit-tab">
      <div className="control-sections">
        <EnvironmentControls
          envDestroyActivated={envDestroyActivated}
          onToggleEnvDestroy={onToggleEnvDestroy}
        />
        <QueueControls
          onAddPlan={onAddPlan}
          onClearQueue={onClearQueue}
        />
        <ExecutionControls
          isRunning={isRunning}
          onStart={onStart}
          onStop={onStop}
        />
        <StatusMonitor status={status} />
      </div>
      <div className="editor-sections">
        <PlanEditor onSavePlan={onSavePlan} />
        <div className="queue-editor-section">
          <RunningPlan plan={runningPlan} />
          <PlanQueue plans={plans} />
          <PlanHistory history={history} />
        </div>
      </div>
    </div>
  );
}

export default App;