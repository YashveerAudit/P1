// Thin wrapper around fetch that talks to the FastAPI backend and turns
// its standard error format into a single ApiError type.

const API_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

export class ApiError extends Error {
  constructor(message, { status = 0, code = 'network_error', details = [] } = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }

  get isNotFound() {
    return this.status === 404;
  }

  /** Map server validation details to { fieldName: message }. */
  fieldErrors() {
    return Object.fromEntries(this.details.map((d) => [d.field, d.message]));
  }
}

export async function request(path, { method = 'GET', body, signal } = {}) {
  let response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      method,
      signal,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (err) {
    if (err.name === 'AbortError') throw err;
    throw new ApiError('Cannot reach the server. Please check your connection and try again.');
  }

  if (response.status === 204) return null;

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const error = data?.error ?? {};
    throw new ApiError(error.message || `Request failed (${response.status}).`, {
      status: response.status,
      code: error.code,
      details: error.details ?? [],
    });
  }

  return data;
}
