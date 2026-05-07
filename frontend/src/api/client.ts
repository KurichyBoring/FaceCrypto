import axios from 'axios';
import type { AuthResponse } from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !window.location.pathname.includes('/login')) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (data: { username: string; password: string }) =>
    api.post<AuthResponse>('/auth/login', data),
  register: (data: { username: string; email: string; password: string; role: string }) =>
    api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
};

export const walletAPI = {
  getBalance: () => api.get('/wallet/balance'),
  transfer: (data: { receiver_username: string; amount: number }) =>
    api.post('/wallet/transfer', data),
  withdraw: (data: { amount: number; address: string }) =>
    api.post('/wallet/withdraw', data),
  getTransactions: (limit?: number) =>
    api.get('/wallet/transactions', { params: { limit } }),
  getExchangeRates: () => api.get('/wallet/exchange-rates'),
};

export const chatAPI = {
  getHistory: (otherUsername: string, limit?: number) =>
    api.get(`/chat/history/${otherUsername}`, { params: { limit } }),
  getUnreadCount: () => api.get('/chat/unread-count'),
  searchUsers: (query: string) =>
    api.get('/chat/search-users', { params: { q: query } }),
};

export const adminAPI = {
  getUsers: (skip?: number, limit?: number) =>
    api.get('/admin/users', { params: { skip, limit } }),
  getStats: () => api.get('/admin/stats'),
  getTransactions: (limit?: number) =>
    api.get('/admin/transactions', { params: { limit } }),
};

export default api;
