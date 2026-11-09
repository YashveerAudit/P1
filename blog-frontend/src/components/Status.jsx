// Small, reusable building blocks for loading / error / empty states.

export function Loading({ label = 'Loading…' }) {
  return (
    <div className="status" role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true" />
      {label}
    </div>
  );
}

export function ErrorMessage({ message, onRetry }) {
  return (
    <div className="alert alert--error" role="alert">
      <span>{message}</span>
      {onRetry && (
        <button type="button" className="btn btn--small" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}

export function EmptyState({ title, children }) {
  return (
    <div className="empty card">
      <h2>{title}</h2>
      {children}
    </div>
  );
}
