import { create } from 'zustand';
import type { ChatMessage, UserSearchResult } from '../types';

interface ChatState {
  messages: ChatMessage[];
  activeChat: string | null;
  unreadCount: number;
  searchResults: UserSearchResult[];
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (msg: ChatMessage) => void;
  setActiveChat: (username: string | null) => void;
  setUnreadCount: (count: number) => void;
  setSearchResults: (results: UserSearchResult[]) => void;
  clearSearchResults: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  activeChat: null,
  unreadCount: 0,
  searchResults: [],
  setMessages: (messages) => set({ messages }),
  addMessage: (msg) =>
    set((state) => ({ messages: [...state.messages, msg] })),
  setActiveChat: (activeChat) => set({ activeChat }),
  setUnreadCount: (unreadCount) => set({ unreadCount }),
  setSearchResults: (searchResults) => set({ searchResults }),
  clearSearchResults: () => set({ searchResults: [] }),
}));
