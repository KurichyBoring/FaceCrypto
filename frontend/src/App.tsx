import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import WalletPage from './pages/WalletPage';
import ChatPage from './pages/ChatPage';
import AdminPage from './pages/AdminPage';
import Layout from './components/Layout';

function ProtectedLayout() {
  const { token, user } = useAuthStore();
  if (!token) return <Navigate to="/login" replace />;
  return <Layout />;
}

export default function App() {
  const token = useAuthStore((s) => s.token);
  const user = useAuthStore((s) => s.user);

  return (
    <Routes>
      <Route path="/login" element={token ? <Navigate to="/wallet" /> : <LoginPage />} />
      <Route path="/register" element={token ? <Navigate to="/wallet" /> : <RegisterPage />} />
      <Route element={<ProtectedLayout />}>
        <Route path="/wallet" element={<WalletPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/admin" element={user?.role === 'admin' ? <AdminPage /> : <Navigate to="/wallet" />} />
      </Route>
      <Route path="/" element={<Navigate to="/wallet" />} />
    </Routes>
  );
}
