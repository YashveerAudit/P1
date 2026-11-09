import { request } from './client';

export const register = (user) => request('/api/auth/register', { method: 'POST', body: user });

export const login = (credentials) => request('/api/auth/login', { method: 'POST', body: credentials });

export const me = (signal) => request('/api/auth/me', { signal });
