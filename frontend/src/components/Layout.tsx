import { Link, Outlet } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export default function Layout() {
  const { user, logout } = useAuthStore();

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{
        background: 'var(--bg-primary)',
        borderBottom: '1px solid var(--border-color)',
        padding: '12px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        boxShadow: 'var(--shadow-sm)'
      }}>
        <Link to="/wallet" style={{ textDecoration: 'none', color: 'var(--text-primary)', fontWeight: 600, fontSize: 18 }}>
          FaceCrypto
        </Link>
        <nav style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
          <Link to="/wallet" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontSize: 14 }}>Wallet</Link>
          <Link to="/chat" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontSize: 14 }}>Chat</Link>
          {user?.role === 'admin' && (
            <Link to="/admin" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontSize: 14 }}>Admin</Link>
          )}
          <span style={{ fontSize: 14, color: 'var(--text-muted)' }}>{user?.username}</span>
          <button onClick={logout} style={{ padding: '4px 12px', fontSize: 13 }}>Logout</button>
        </nav>
      </header>
      <main style={{ flex: 1, padding: '24px', maxWidth: 1200, width: '100%', margin: '0 auto' }}>
        <Outlet />
      </main>
    </div>
  );
}
