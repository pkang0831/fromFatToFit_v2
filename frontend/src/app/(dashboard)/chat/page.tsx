'use client';

import { useState, useEffect, useRef } from 'react';
import toast from 'react-hot-toast';
import { Send, Trash2, MessageCircle, Bot, User, Zap } from 'lucide-react';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { chatApi } from '@/lib/api/services';

interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  created_at?: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [messagesToday, setMessagesToday] = useState(0);
  const [dailyLimit, setDailyLimit] = useState(15);
  const [error, setError] = useState<string | null>(null);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const remaining = Math.max(0, dailyLimit - messagesToday);

  useEffect(() => {
    loadHistory();
    fetchStatus();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchStatus = async () => {
    try {
      const res = await chatApi.getStatus();
      setMessagesToday(res.data.messages_today);
      setDailyLimit(res.data.daily_limit);
    } catch {
      // ignore
    }
  };

  const loadHistory = async () => {
    try {
      setIsLoadingHistory(true);
      const res = await chatApi.getHistory(50);
      setMessages(res.data as ChatMessage[]);
    } catch {
      // No history yet
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    if (remaining <= 0) {
      setError(`Daily limit reached (${dailyLimit}/day). Come back tomorrow!`);
      return;
    }

    setError(null);
    const userMsg: ChatMessage = { role: 'user', content: trimmed };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await chatApi.sendMessage(trimmed);
      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: res.data.answer,
        sources: res.data.sources,
      };
      setMessages(prev => [...prev, assistantMsg]);
      setMessagesToday(res.data.messages_today);
      setDailyLimit(res.data.daily_limit);
    } catch (err: any) {
      if (err.response?.status === 429) {
        setError('Daily message limit reached. Come back tomorrow!');
      } else {
        setError(err.response?.data?.detail || 'Failed to send message');
      }
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleClear = async () => {
    try {
      await chatApi.clearHistory();
      setMessages([]);
      toast.success('Chat history cleared');
    } catch {
      toast.error('Failed to clear history');
      setError('Failed to clear history');
    } finally {
      setShowClearConfirm(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-80px)] max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-gray-700 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
            <Bot className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900 dark:text-white dark:text-white">AI Coach</h1>
            <p className="text-xs text-gray-600 dark:text-gray-400 dark:text-gray-400">Free — ask anything about diet & fitness</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 dark:bg-emerald-950 border border-emerald-200 dark:border-emerald-800 rounded-lg">
            <Zap className="w-4 h-4 text-emerald-600" />
            <span className="text-sm font-semibold text-emerald-700 dark:text-emerald-300">
              {remaining}
            </span>
            <span className="text-xs text-emerald-500 dark:text-emerald-400">/ {dailyLimit} today</span>
          </div>
          {messages.length > 0 && (
            <button
              onClick={() => setShowClearConfirm(true)}
              className="p-2 text-gray-600 dark:text-gray-400 hover:text-error rounded-lg hover:bg-error/10 transition-colors"
              title="Clear chat"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      <ConfirmDialog
        isOpen={showClearConfirm}
        onClose={() => setShowClearConfirm(false)}
        onConfirm={handleClear}
        title="Clear Chat History"
        message="Are you sure you want to clear all chat history? This cannot be undone."
        confirmText="Clear"
        variant="warning"
      />

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {isLoadingHistory ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          </div>
        ) : messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
              <MessageCircle className="w-8 h-8 text-primary" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white dark:text-white mb-2">Ask me anything about diet & fitness</h2>
            <p className="text-gray-600 dark:text-gray-400 dark:text-gray-400 text-sm max-w-md mb-1">
              I&apos;m trained on hundreds of expert diet coaching videos. Ask about weight loss, nutrition, exercise, body composition, and more.
            </p>
            <p className="text-emerald-600 text-xs font-medium mb-6">
              Free — {dailyLimit} messages per day
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-lg">
              {[
                'How can I lose belly fat effectively?',
                'Is intermittent fasting good for weight loss?',
                'How many calories should I eat to lose weight?',
                'Why am I not losing weight even though I exercise?',
              ].map((q) => (
                <button
                  key={q}
                  onClick={() => { setInput(q); inputRef.current?.focus(); }}
                  className="text-left text-sm px-4 py-3 bg-gray-100 dark:bg-gray-700 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 dark:border-gray-700 rounded-xl hover:border-primary hover:bg-primary/5 transition-colors text-gray-600 dark:text-gray-400 dark:text-gray-400"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div
              key={i}
              className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <Bot className="w-4 h-4 text-primary" />
                </div>
              )}
              <div
                className={`max-w-[75%] rounded-2xl px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-primary text-white rounded-br-md'
                    : 'bg-gray-100 dark:bg-gray-700 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 dark:border-gray-700 text-gray-900 dark:text-white dark:text-white rounded-bl-md'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0 mt-1">
                  <User className="w-4 h-4 text-white" />
                </div>
              )}
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
              <Bot className="w-4 h-4 text-primary" />
            </div>
            <div className="bg-gray-100 dark:bg-gray-700 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 dark:border-gray-700 rounded-2xl rounded-bl-md px-4 py-3">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-text-secondary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-text-secondary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-text-secondary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error */}
      {error && (
        <div className="mx-4 mb-2 p-3 bg-error/10 border border-error rounded-lg">
          <p className="text-sm text-error">{error}</p>
        </div>
      )}

      {/* Input */}
      <div data-tour="chat-input" className="px-4 py-3 border-t border-gray-100 dark:border-gray-700 dark:border-gray-700 bg-white dark:bg-gray-800 dark:bg-gray-900">
        <div className="flex items-end gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about diet, nutrition, exercise..."
            rows={1}
            className="flex-1 resize-none rounded-xl border border-gray-100 dark:border-gray-700 dark:border-gray-600 bg-gray-100 dark:bg-gray-700 dark:bg-gray-800 px-4 py-3 text-sm text-gray-900 dark:text-white dark:text-white placeholder:text-gray-500 dark:text-gray-500 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent max-h-32"
            style={{ minHeight: '44px' }}
            disabled={isLoading || remaining <= 0}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading || remaining <= 0}
            className="p-3 rounded-xl bg-primary text-white hover:bg-primary/90 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex-shrink-0"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-500 dark:text-gray-500 mt-1.5 text-center">
          {remaining > 0
            ? `${remaining} messages remaining today`
            : 'Daily limit reached — resets at midnight'}
        </p>
      </div>
    </div>
  );
}
