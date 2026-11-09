// Thin wrapper around fetch that talks to the FastAPI backend and turns
// its standard error format into a single ApiError type.
import { getToken } from './token';

const API_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

// AuthContext registers a handler here so an expired session signs the user out
// wherever the 401 happens, without every page needing to know about it.
let onSessionExpired = () => {};
export function setSessionExpiredHandler(handler) {
  onSessionExpired = handler;
}

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
  const headers = {};
  if (body) headers['Content-Type'] = 'application/json';
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      method,
      signal,
      headers,
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
    // "not_authenticated" means our token is missing/expired (not a wrong password).
    if (response.status === 401 && error.code === 'not_authenticated' && token) {
      onSessionExpired();
    }
    throw new ApiError(error.message || `Request failed (${response.status}).`, {
      status: response.status,
      code: error.code,
      details: error.details ?? [],
    });
  }

  return data;
}
