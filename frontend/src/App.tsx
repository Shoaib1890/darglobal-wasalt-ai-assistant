import React, { useState, useEffect, useRef } from 'react';
import { Header } from './components/Header';
import { SuggestedQuestions } from './components/SuggestedQuestions';
import { ChatMessageBubble } from './components/ChatMessageBubble';
import { ChatInput } from './components/ChatInput';
import { Footer } from './components/Footer';
import { ChatMessage, HealthStatus } from './types';
import { fetchHealth, sendChatMessage } from './services/api';
import { formatTimestamp } from './utils/text';
import { Sparkles } from 'lucide-react';

export const App: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isLoadingHealth, setIsLoadingHealth] = useState<boolean>(true);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Poll health on mount
  useEffect(() => {
    let isMounted = true;
    const checkHealth = async () => {
      try {
        const h = await fetchHealth();
        if (isMounted) {
          setHealth(h);
          setIsLoadingHealth(false);
        }
      } catch (err: any) {
        if (isMounted) {
          setIsLoadingHealth(false);
          // Backend might be offline or starting up
          console.warn('Backend health check error:', err.message);
        }
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 20000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  // Auto-scroll to bottom on messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSendMessage = async (text: string) => {
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: formatTimestamp(),
    };

    // Append user message
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    // Format conversation history for FastAPI backend
    const historyPayload = messages.map((m) => ({
      role: m.role,
      content: m.content,
    }));

    try {
      const response = await sendChatMessage({
        message: text,
        history: historyPayload,
        top_k: 4,
      });

      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.answer,
        timestamp: formatTimestamp(),
        citations: response.citations,
        grounded: response.grounded,
        modelUsed: response.model_used,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      console.error('Chat error:', err);
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `Error: Unable to connect to the backend assistant (${err.message || 'Network error'}). Please ensure the FastAPI server is running.`,
        timestamp: formatTimestamp(),
        isError: true,
        grounded: false,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearConversation = () => {
    setMessages([]);
  };

  return (
    <div className="flex flex-col h-screen bg-[#FAF9F6] text-stone-900 overflow-hidden">
      {/* Top Header */}
      <Header
        health={health}
        isLoadingHealth={isLoadingHealth}
        onClear={handleClearConversation}
        hasMessages={messages.length > 0}
      />

      {/* Main Chat Scroll Area */}
      <main className="flex-1 overflow-y-auto px-4 sm:px-6 py-4">
        <div className="max-w-4xl mx-auto min-h-full flex flex-col justify-between">
          {messages.length === 0 ? (
            <div className="my-auto">
              <SuggestedQuestions onSelect={handleSendMessage} />
            </div>
          ) : (
            <div className="space-y-1 pb-4">
              {messages.map((msg) => (
                <ChatMessageBubble key={msg.id} message={msg} />
              ))}

              {/* Typing / Loading Indicator */}
              {isLoading && (
                <div className="flex justify-start items-center gap-2.5 my-3 pl-1">
                  <div className="w-8 h-8 rounded-xl bg-emerald-800 text-white flex items-center justify-center shrink-0 shadow-xs">
                    <Sparkles className="w-4 h-4 animate-spin text-emerald-200" />
                  </div>
                  <div className="bg-white rounded-2xl rounded-tl-xs px-4 py-3 border border-stone-200/80 shadow-xs flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-700 animate-bounce [animation-delay:-0.3s]" />
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-700 animate-bounce [animation-delay:-0.15s]" />
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-700 animate-bounce" />
                    <span className="text-xs text-stone-700 font-medium ml-2">
                      Consulting verified knowledge...
                    </span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </main>

      {/* Bottom Sticky Input */}
      <ChatInput onSend={handleSendMessage} isLoading={isLoading} />

      {/* Subtle Footer */}
      <Footer />
    </div>
  );
};

export default App;
