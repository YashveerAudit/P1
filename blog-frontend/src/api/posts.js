import { request } from './client';

export const listPosts = ({ skip = 0, limit = 9 } = {}, signal) =>
  request(`/api/posts?skip=${skip}&limit=${limit}`, { signal });

export const getPost = (id, signal) =>
  request(`/api/posts/${encodeURIComponent(id)}`, { signal });

export const createPost = (post) =>
  request('/api/posts', { method: 'POST', body: post });

export const updatePost = (id, post) =>
  request(`/api/posts/${encodeURIComponent(id)}`, { method: 'PUT', body: post });

export const deletePost = (id) =>
  request(`/api/posts/${encodeURIComponent(id)}`, { method: 'DELETE' });
