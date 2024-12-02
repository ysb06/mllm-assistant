import './SessionManager.scss';

export interface SessionInfo {
  isConnected: boolean;
  startTime: string;
  sessionId: string;
}

interface SessionManagerProps {
  sessionInfo: SessionInfo;
}

export function SessionManager({ sessionInfo }: SessionManagerProps) {
  return (
    <div data-component="SessionManager">
      <h2>Session Information</h2>
      <ul>
        <li>
          <strong>Status:</strong>{' '}
          {sessionInfo.isConnected ? 'Connected' : 'Disconnected'}
        </li>
        <li>
          <strong>Start Time:</strong> {sessionInfo.startTime}
        </li>
        <li>
          <strong>Server URL:</strong> {sessionInfo.sessionId}
        </li>
      </ul>
    </div>
  );
}

export default SessionManager;