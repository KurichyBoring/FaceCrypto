import { useEffect, useState, useRef } from 'react';
import { chatAPI } from '../api/client';
import { useChatStore } from '../store/chatStore';
import { useWebSocket } from '../hooks/useWebSocket';
import type { ChatMessage, UserSearchResult } from '../types';

export default function ChatPage() {
  const { messages, activeChat, setMessages, addMessage, setActiveChat, setSearchResults, searchResults, clearSearchResults } = useChatStore();
  const [messageText, setMessageText] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { sendMessage } = useWebSocket();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  async function loadChatHistory(username: string) {
    try {
      const res = await chatAPI.getHistory(username);
      setMessages(res.data);
      setActiveChat(username);
    } catch (e) {
      console.error('Failed to load chat history', e);
    }
  }

  async function handleSearch(e: React.ChangeEvent<HTMLInputElement>) {
    const query = e.target.value;
    setSearchQuery(query);
    if (query.length >= 2) {
      try {
        const res = await chatAPI.searchUsers(query);
        setSearchResults(res.data);
      } catch (e) {
        console.error('Search failed', e);
      }
    } else {
      clearSearchResults();
    }
  }

  function handleSendMessage(e: React.FormEvent) {
    e.preventDefault();
    if (!messageText.trim() || !activeChat) return;
    sendMessage(activeChat, messageText.trim());
    setMessageText('');
  }

  return (
    <div className="card" style={{ display: 'flex', height: 'calc(100vh - 140px)', minHeight: 500 }}>
      <div style={{ width: 280, borderRight: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: 12, borderBottom: '1px solid var(--border-color)' }}>
          <input
            placeholder="Search users..."
            value={searchQuery}
            onChange={handleSearch}
            style={{ fontSize: 13 }}
          />
        </div>
        <div style={{ flex: 1, overflowY: 'auto' }}>
          {searchResults.map(user => (
            <div
              key={user.id}
              onClick={() => loadChatHistory(user.username)}
              style={{
                padding: '10px 12px',
                cursor: 'pointer',
                background: activeChat === user.username ? 'var(--bg-secondary)' : 'transparent',
                borderBottom: '1px solid var(--bg-tertiary)',
                fontSize: 14
              }}
            >
              {user.username}
              <span style={{ color: 'var(--text-muted)', fontSize: 11, marginLeft: 6 }}>{user.role}</span>
            </div>
          ))}
        </div>
      </div>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {activeChat ? (
          <>
            <div style={{ padding: 12, borderBottom: '1px solid var(--border-color)', fontWeight: 600, fontSize: 14 }}>
              {activeChat}
            </div>
            <div style={{ flex: 1, overflowY: 'auto', padding: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
              {messages.map(msg => (
                <div
                  key={msg.id}
                  style={{
                    alignSelf: msg.sender_username === activeChat ? 'flex-end' : 'flex-start',
                    background: msg.sender_username === activeChat ? 'var(--accent)' : 'var(--bg-secondary)',
                    color: msg.sender_username === activeChat ? 'white' : 'var(--text-primary)',
                    padding: '8px 12px',
                    borderRadius: 'var(--radius)',
                    maxWidth: '70%',
                    fontSize: 14
                  }}
                >
                  <div>{msg.content}</div>
                  <div style={{ fontSize: 11, opacity: 0.7, marginTop: 4 }}>
                    {new Date(msg.created_at).toLocaleTimeString()}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            <form onSubmit={handleSendMessage} style={{ padding: 12, borderTop: '1px solid var(--border-color)', display: 'flex', gap: 8 }}>
              <input
                value={messageText}
                onChange={e => setMessageText(e.target.value)}
                placeholder="Type a message..."
                style={{ flex: 1 }}
              />
              <button className="primary" type="submit" disabled={!messageText.trim()}>Send</button>
            </form>
          </>
        ) : (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: 14 }}>
            Select a user to start chatting
          </div>
        )}
      </div>
    </div>
  );
}
