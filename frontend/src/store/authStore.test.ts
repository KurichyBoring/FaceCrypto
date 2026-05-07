import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useAuthStore } from './authStore'

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key]
    }),
    clear: vi.fn(() => {
      store = {}
    }),
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

// Test authStore logic
describe('authStore', () => {
  beforeEach(() => {
    localStorageMock.clear()
    vi.clearAllMocks()
    // Reset store state
    useAuthStore.setState({ token: null, user: null })
  })

  it('should initialize with null token and user', () => {
    const state = useAuthStore.getState()
    expect(state.token).toBeNull()
    expect(state.user).toBeNull()
  })

  it('should set auth data', () => {
    const { setAuth } = useAuthStore.getState()

    setAuth('test-token', {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      role: 'user',
      wallet_address: '0x123',
      balance: 10000,
      is_active: true,
      created_at: '2024-01-01',
    })

    const state = useAuthStore.getState()
    expect(state.token).toBe('test-token')
    expect(state.user?.username).toBe('testuser')
  })

  it('should logout and clear data', () => {
    const { setAuth, logout } = useAuthStore.getState()

    setAuth('test-token', {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      role: 'user',
      wallet_address: '0x123',
      balance: 10000,
      is_active: true,
      created_at: '2024-01-01',
    })

    logout()

    const state = useAuthStore.getState()
    expect(state.token).toBeNull()
    expect(state.user).toBeNull()
  })
})
