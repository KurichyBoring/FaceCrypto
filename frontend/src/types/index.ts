export type UserRole = 'user' | 'admin';

export interface User {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  wallet_address: string;
  balance: number;
  is_active: boolean;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  role: UserRole;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface Transaction {
  id: number;
  hash: string;
  sender_id: number | null;
  receiver_id: number | null;
  amount: number;
  fee: number;
  tx_type: 'transfer' | 'withdrawal' | 'deposit';
  status: 'pending' | 'completed' | 'failed';
  created_at: string;
  sender_username?: string;
  receiver_username?: string;
}

export interface TransactionRequest {
  receiver_username?: string;
  amount: number;
  address?: string;
}

export interface ChatMessage {
  id: number;
  sender_id: number;
  receiver_id: number;
  sender_username: string;
  receiver_username: string;
  content: string;
  is_read: boolean;
  created_at: string;
}

export interface ChatMessageRequest {
  receiver_username: string;
  content: string;
}

export interface ExchangeRate {
  btc_usd: number;
  eth_usd: number;
  updated_at: string;
}

export interface UserSearchResult {
  id: number;
  username: string;
  role: UserRole;
}

export interface AdminStats {
  total_users: number;
  total_transactions: number;
  total_volume: number;
}
