// The login token lives in localStorage so a page refresh keeps you signed in.
// Trade-off: localStorage is readable by any script on the page, so this relies
// on the app never rendering untrusted HTML (React escapes everything by default).
// An httpOnly cookie would be the next step for a production system.

const KEY = 'blog.token';

export function getToken() {
  try {
    return localStorage.getItem(KEY);
  } catch {
    return null;
  }
}

export function setToken(token) {
  try {
    if (token) localStorage.setItem(KEY, token);
    else localStorage.removeItem(KEY);
  } catch {
    // Storage unavailable (private mode, blocked): the session just won't persist.
  }
}
