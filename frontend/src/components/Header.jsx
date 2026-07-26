export default function Header({ connected, mode }) {
  return (
    <header className="app-header glass">
      <div className="brand">
        <span className="brand-icon" aria-hidden="true">
          🔧
        </span>
        <h1 className="brand-title">AI Operations Copilot</h1>
      </div>
      <div
        className={`status-badge ${connected ? "status-live" : "status-offline"}`}
        title={mode || (connected ? "Connected" : "API unreachable")}
      >
        <span className="status-dot" aria-hidden="true" />
        <span className="status-label">
          {connected ? "Live" : "Offline"}
        </span>
      </div>
    </header>
  );
}
