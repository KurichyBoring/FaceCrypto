import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../api/client';
import { useAuthStore } from '../store/authStore';
import type { RegisterRequest, LoginRequest } from '../types';

export function useAuth() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { setAuth } = useAuthStore();
  const navigate = useNavigate();

  const login = useCallback(async (data: LoginRequest) => {
    setLoading(true);
    setError(null);
    try {
      const res = await authAPI.login(data);
      const { access_token } = res.data;
      localStorage.setItem('token', access_token);

      const userRes = await authAPI.me();
      setAuth(access_token, userRes.data);
      navigate(userRes.data.role === 'admin' ? '/admin' : '/wallet');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  }, [setAuth, navigate]);

  const register = useCallback(async (data: RegisterRequest) => {
    setLoading(true);
    setError(null);
    try {
      await authAPI.register(data);
      await login({ username: data.username, password: data.password });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
      setLoading(false);
    }
  }, [login]);

  return { login, register, loading, error };
}
