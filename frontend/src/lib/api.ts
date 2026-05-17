import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('nlc-session') : null;
    if (token) {
      try {
        const session = JSON.parse(token);
        if (session?.session?.accessToken) {
          config.headers.Authorization = `Bearer ${session.session.accessToken}`;
        }
      } catch {
        // Token parse failed, continue without it
      }
    }
    return config;
  },
  (error) => Promise.reject(error),
);

export function setAuthToken(token?: string) {
  if (!token) {
    delete api.defaults.headers.common.Authorization;
    return;
  }
  api.defaults.headers.common.Authorization = `Bearer ${token}`;
}

export function withAuth(token?: string) {
  return {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  };
}

export const authApi = {
  login: (credentials: { email: string; password: string }) =>
    api.post('/auth/login', credentials),

  register: (credentials: { email: string; password: string; fullName: string }) =>
    api.post('/auth/register', credentials),

  me: () => api.get('/auth/me'),
};
