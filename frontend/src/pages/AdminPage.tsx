import { useEffect, useState } from 'react';
import { adminAPI } from '../api/client';
import type { User, Transaction, AdminStats } from '../types';

export default function AdminPage() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [activeTab, setActiveTab] = useState<'stats' | 'users' | 'transactions'>('stats');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      const [statsRes, usersRes, txRes] = await Promise.all([
        adminAPI.getStats(),
        adminAPI.getUsers(0, 100),
        adminAPI.getTransactions(100)
      ]);
      setStats(statsRes.data);
      setUsers(usersRes.data);
      setTransactions(txRes.data);
    } catch (e) {
      console.error('Failed to load admin data', e);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <p>Loading admin panel...</p>;

  return (
    <div>
      <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 20 }}>Admin Panel</h2>

      <div style={{ display: 'flex', gap: 0, borderBottom: '1px solid var(--border-color)', marginBottom: 20 }}>
        {(['stats', 'users', 'transactions'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '8px 16px',
              border: 'none',
              borderBottom: activeTab === tab ? '2px solid var(--accent)' : '2px solid transparent',
              background: 'none',
              color: activeTab === tab ? 'var(--accent)' : 'var(--text-secondary)',
              fontWeight: activeTab === tab ? 600 : 400,
              borderRadius: 0
            }}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {activeTab === 'stats' && stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
          <div className="card">
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 8 }}>Total Users</div>
            <div style={{ fontSize: 28, fontWeight: 700 }}>{stats.total_users}</div>
          </div>
          <div className="card">
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 8 }}>Total Transactions</div>
            <div style={{ fontSize: 28, fontWeight: 700 }}>{stats.total_transactions}</div>
          </div>
          <div className="card">
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 8 }}>Total Volume</div>
            <div style={{ fontSize: 28, fontWeight: 700 }}>${stats.total_volume.toLocaleString()}</div>
          </div>
        </div>
      )}

      {activeTab === 'users' && (
        <div className="card" style={{ padding: 0 }}>
          <table style={{ width: '100%', fontSize: 13, borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left' }}>
                <th style={{ padding: '10px 12px' }}>ID</th>
                <th style={{ padding: '10px 12px' }}>Username</th>
                <th style={{ padding: '10px 12px' }}>Email</th>
                <th style={{ padding: '10px 12px' }}>Role</th>
                <th style={{ padding: '10px 12px' }}>Balance</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id} style={{ borderBottom: '1px solid var(--bg-tertiary)' }}>
                  <td style={{ padding: '8px 12px' }}>{u.id}</td>
                  <td style={{ padding: '8px 12px' }}>{u.username}</td>
                  <td style={{ padding: '8px 12px' }}>{u.email}</td>
                  <td style={{ padding: '8px 12px' }}>{u.role}</td>
                  <td style={{ padding: '8px 12px' }}>${u.balance.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'transactions' && (
        <div className="card" style={{ padding: 0 }}>
          <table style={{ width: '100%', fontSize: 13, borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left' }}>
                <th style={{ padding: '10px 12px' }}>Hash</th>
                <th style={{ padding: '10px 12px' }}>Type</th>
                <th style={{ padding: '10px 12px' }}>Amount</th>
                <th style={{ padding: '10px 12px' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map(tx => (
                <tr key={tx.id} style={{ borderBottom: '1px solid var(--bg-tertiary)' }}>
                  <td style={{ padding: '8px 12px', fontFamily: 'var(--font-mono)', fontSize: 12 }}>{tx.hash.slice(0, 20)}...</td>
                  <td style={{ padding: '8px 12px' }}>{tx.tx_type}</td>
                  <td style={{ padding: '8px 12px' }}>${tx.amount.toLocaleString()}</td>
                  <td style={{ padding: '8px 12px' }} className={`status-${tx.status}`}>{tx.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
