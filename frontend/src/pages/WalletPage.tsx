import { useEffect, useState } from 'react';
import { walletAPI } from '../api/client';
import { useAuthStore } from '../store/authStore';
import { useWalletStore } from '../store/walletStore';
import type { Transaction, ExchangeRate } from '../types';

export default function WalletPage() {
  const { user, updateBalance } = useAuthStore();
  const { transactions, setTransactions, addTransaction } = useWalletStore();
  const [activeTab, setActiveTab] = useState<'balance' | 'transfer' | 'withdraw' | 'history'>('balance');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);

  const [transferData, setTransferData] = useState({ receiver_username: '', amount: '' });
  const [withdrawData, setWithdrawData] = useState({ amount: '', address: '' });
  const [exchangeRates, setExchangeRates] = useState<ExchangeRate | null>(null);

  useEffect(() => {
    loadTransactions();
    loadExchangeRates();
  }, []);

  async function loadTransactions() {
    setLoading(true);
    try {
      const res = await walletAPI.getTransactions(50);
      setTransactions(res.data);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Failed to load transactions');
    } finally {
      setLoading(false);
    }
  }

  async function loadExchangeRates() {
    try {
      const res = await walletAPI.getExchangeRates();
      setExchangeRates(res.data);
    } catch (e) {
      console.error('Failed to load rates');
    }
  }

  async function handleTransfer(e: React.FormEvent) {
    e.preventDefault();
    setProcessing(true);
    setError(null);
    try {
      const res = await walletAPI.transfer({
        receiver_username: transferData.receiver_username,
        amount: parseFloat(transferData.amount)
      });
      addTransaction(res.data);
      updateBalance(user!.balance - parseFloat(transferData.amount) * 1.01);
      setTransferData({ receiver_username: '', amount: '' });
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Transfer failed');
    } finally {
      setProcessing(false);
    }
  }

  async function handleWithdraw(e: React.FormEvent) {
    e.preventDefault();
    setProcessing(true);
    setError(null);
    try {
      const res = await walletAPI.withdraw({
        amount: parseFloat(withdrawData.amount),
        address: withdrawData.address
      });
      addTransaction(res.data);
      setWithdrawData({ amount: '', address: '' });
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Withdrawal failed');
    } finally {
      setProcessing(false);
    }
  }

  return (
    <div>
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h2 style={{ fontSize: 20, fontWeight: 600 }}>Wallet</h2>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 13, color: 'var(--text-muted)' }}>
            {user?.wallet_address?.slice(0, 20)}...
          </span>
        </div>
        <div style={{ fontSize: 32, fontWeight: 700, marginBottom: 8 }}>
          ${user?.balance?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </div>
        <div style={{ display: 'flex', gap: 12, fontSize: 13, color: 'var(--text-secondary)' }}>
          <span>BTC: ${exchangeRates?.btc_usd || '...'}</span>
          <span>ETH: ${exchangeRates?.eth_usd || '...'}</span>
        </div>
      </div>

      <div className="card">
        <div style={{ display: 'flex', gap: 0, borderBottom: '1px solid var(--border-color)', marginBottom: 20 }}>
          {(['balance', 'transfer', 'withdraw', 'history'] as const).map(tab => (
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

        {error && <div className="error-text" style={{ marginBottom: 12 }}>{error}</div>}

        {activeTab === 'transfer' && (
          <form onSubmit={handleTransfer}>
            <div className="form-group">
              <label>Recipient Username</label>
              <input
                value={transferData.receiver_username}
                onChange={e => setTransferData({ ...transferData, receiver_username: e.target.value })}
                placeholder="Enter username"
                required
              />
            </div>
            <div className="form-group">
              <label>Amount</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                value={transferData.amount}
                onChange={e => setTransferData({ ...transferData, amount: e.target.value })}
                placeholder="0.00"
                required
              />
              <small style={{ color: 'var(--text-muted)', fontSize: 12 }}>Fee: 1% (simulated)</small>
            </div>
            <button className="primary" disabled={processing} style={{ width: '100%' }}>
              {processing ? 'Processing...' : 'Send'}
            </button>
          </form>
        )}

        {activeTab === 'withdraw' && (
          <form onSubmit={handleWithdraw}>
            <div className="form-group">
              <label>Amount</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                value={withdrawData.amount}
                onChange={e => setWithdrawData({ ...withdrawData, amount: e.target.value })}
                placeholder="0.00"
                required
              />
              <small style={{ color: 'var(--text-muted)', fontSize: 12 }}>Fee: 2% (simulated)</small>
            </div>
            <div className="form-group">
              <label>Withdrawal Address</label>
              <input
                value={withdrawData.address}
                onChange={e => setWithdrawData({ ...withdrawData, address: e.target.value })}
                placeholder="Enter wallet address"
                required
              />
            </div>
            <button className="primary" disabled={processing} style={{ width: '100%' }}>
              {processing ? 'Processing...' : 'Withdraw'}
            </button>
          </form>
        )}

        {activeTab === 'history' && (
          <div>
            {loading ? <p>Loading...</p> : (
              <table style={{ width: '100%', fontSize: 13, borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left' }}>
                    <th style={{ padding: '8px 4px' }}>Hash</th>
                    <th style={{ padding: '8px 4px' }}>Type</th>
                    <th style={{ padding: '8px 4px' }}>Amount</th>
                    <th style={{ padding: '8px 4px' }}>Status</th>
                    <th style={{ padding: '8px 4px' }}>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map(tx => (
                    <tr key={tx.id} style={{ borderBottom: '1px solid var(--bg-tertiary)' }}>
                      <td style={{ padding: '8px 4px', fontFamily: 'var(--font-mono)', fontSize: 12 }}>
                        {tx.hash.slice(0, 16)}...
                      </td>
                      <td style={{ padding: '8px 4px' }}>{tx.tx_type}</td>
                      <td style={{ padding: '8px 4px' }}>${tx.amount.toLocaleString()}</td>
                      <td style={{ padding: '8px 4px' }} className={`status-${tx.status}`}>{tx.status}</td>
                      <td style={{ padding: '8px 4px', color: 'var(--text-muted)' }}>
                        {new Date(tx.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
