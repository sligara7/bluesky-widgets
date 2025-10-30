import React from 'react';

interface ConnectionProps {
  isConnected: boolean;
  onConnect: () => void;
  onDisconnect: () => void;
}

const Connection: React.FC<ConnectionProps> = ({ isConnected, onConnect, onDisconnect }) => {
  return (
    <div className="connection-section">
      <h2>Queue Server Connection</h2>
      <div className="connection-status">
        <span className={`status-indicator ${isConnected ? 'online' : 'offline'}`}>
          {isConnected ? 'ONLINE' : 'OFFLINE'}
        </span>
        <button onClick={onConnect} disabled={isConnected}>Connect</button>
        <button onClick={onDisconnect} disabled={!isConnected}>Disconnect</button>
      </div>
    </div>
  );
};

export default Connection;