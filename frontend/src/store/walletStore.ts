import { create } from 'zustand';
import type { Transaction, ExchangeRate } from '../types';

interface WalletState {
  transactions: Transaction[];
  exchangeRates: ExchangeRate | null;
  isLoading: boolean;
  setTransactions: (txs: Transaction[]) => void;
  addTransaction: (tx: Transaction) => void;
  setExchangeRates: (rates: ExchangeRate) => void;
  setLoading: (loading: boolean) => void;
}

export const useWalletStore = create<WalletState>((set) => ({
  transactions: [],
  exchangeRates: null,
  isLoading: false,
  setTransactions: (transactions) => set({ transactions }),
  addTransaction: (tx) =>
    set((state) => ({ transactions: [tx, ...state.transactions] })),
  setExchangeRates: (exchangeRates) => set({ exchangeRates }),
  setLoading: (isLoading) => set({ isLoading }),
}));
