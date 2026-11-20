import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, isLoading }) => {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [text]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full bg-[#FAF9F6]/95 backdrop-blur-md border-t border-stone-200/80 p-3 sm:p-4">
      <div className="max-w-4xl mx-auto">
        <form
          onSubmit={handleSubmit}
          className="relative flex items-end gap-2 bg-white rounded-2xl border border-stone-300/90 shadow-xs focus-within:border-emerald-700 focus-within:ring-2 focus-within:ring-emerald-700/10 transition-all p-1.5 sm:p-2"
        >
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about DAR Global or Wasalt real estate (English or العربية)..."
            rows={1}
            disabled={isLoading}
            className="flex-1 max-h-40 min-h-[44px] p-2.5 text-sm text-stone-900 placeholder:text-stone-400 bg-transparent resize-none focus:outline-none"
          />

          <button
            type="submit"
            disabled={!text.trim() || isLoading}
            className={`w-9 h-9 rounded-xl flex items-center justify-center transition-all shrink-0 ${
              text.trim() && !isLoading
                ? 'bg-emerald-800 text-white hover:bg-emerald-900 shadow-sm shadow-emerald-900/15 cursor-pointer'
                : 'bg-stone-100 text-stone-400 cursor-not-allowed'
            }`}
            title="Send message (Enter)"
          >
            <ArrowUp className="w-4 h-4 stroke-[2.5]" />
          </button>
        </form>

        <div className="hidden sm:flex items-center justify-between text-[11px] text-stone-600 mt-1.5 px-2">
          <span>Press <strong>Enter</strong> to send, <strong>Shift + Enter</strong> for newline</span>
          <span>Bilingual: Arabic & English</span>
        </div>
      </div>
    </div>
  );
};
