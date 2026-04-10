import { useState, useRef, useEffect } from 'react';
import { Send, MessageSquare, Trash2 } from 'lucide-react';
import { useChat } from '../hooks/useChat';
import type { ChatMessage } from '../types';

interface Props {
  sessionId: string;
}

const SUGGESTED_PROMPTS = [
  'Which stock should I watch tomorrow?',
  'Explain my portfolio health score',
  'What are my biggest risks right now?',
  'How should I rebalance my portfolio?',
];

export default function ChatPanel({ sessionId }: Props) {
  const { messages, isStreaming, error, sendMessage, clearChat } = useChat(sessionId);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim() || isStreaming) return;
    sendMessage(input);
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handlePromptClick = (prompt: string) => {
    sendMessage(prompt);
  };

  return (
    <div className="border border-gray-200 border-l-4 border-l-green-400 bg-white">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-green-500" strokeWidth={1.5} />
          <h3 className="text-sm font-semibold uppercase tracking-wide text-[#6B7280]">
            Chat with your Portfolio
          </h3>
        </div>
        {messages.length > 0 && (
          <button
            onClick={clearChat}
            className="text-xs text-[#9CA3AF] hover:text-[#6B7280] transition-colors flex items-center gap-1"
          >
            <Trash2 className="h-3 w-3" /> Clear
          </button>
        )}
      </div>

      {/* Messages area */}
      <div className="h-96 overflow-y-auto px-5 py-4 space-y-3">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center">
            <p className="text-sm text-[#9CA3AF] mb-4">Ask anything about your portfolio</p>
            <div className="flex flex-wrap gap-2 justify-center max-w-md">
              {SUGGESTED_PROMPTS.map((prompt, i) => (
                <button
                  key={i}
                  onClick={() => handlePromptClick(prompt)}
                  className="text-xs text-[#6B7280] border border-gray-200 px-3 py-1.5 hover:border-green-300 hover:text-green-600 hover:bg-green-50 transition-all"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} isStreaming={isStreaming} />
            ))}
            {error && (
              <div className="text-xs text-red-500 px-3 py-2 bg-red-50 border border-red-200">
                {error}
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input area */}
      <div className="border-t border-gray-200 px-5 py-3 flex gap-2">
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={isStreaming ? 'Waiting for response...' : 'Ask about your portfolio...'}
          disabled={isStreaming}
          className="flex-1 border border-gray-200 bg-white px-3 py-2 text-sm text-[#111827] placeholder:text-[#9CA3AF] focus:outline-none focus:border-green-400 disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || isStreaming}
          className="bg-green-500 text-white px-4 py-2 hover:bg-green-600 transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center"
        >
          <Send className="h-4 w-4" strokeWidth={1.5} />
        </button>
      </div>
    </div>
  );
}

function MessageBubble({ message, isStreaming }: { message: ChatMessage; isStreaming: boolean }) {
  const isUser = message.role === 'user';
  const isLastAssistant = !isUser && isStreaming && message.content !== '';
  const isEmpty = !isUser && message.content === '';

  if (isEmpty && !isStreaming) return null;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] px-3 py-2 text-sm leading-relaxed ${
          isUser
            ? 'bg-green-50 text-[#111827] border border-green-200'
            : 'bg-[#F8FAF9] text-[#374151] border border-gray-200'
        }`}
      >
        {isEmpty && isStreaming ? (
          <span className="text-green-500 animate-subtle-pulse text-sm">▌</span>
        ) : (
          <div className="whitespace-pre-wrap break-words">
            {message.content}
            {isLastAssistant && (
              <span className="text-green-500 animate-subtle-pulse ml-0.5">▌</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
