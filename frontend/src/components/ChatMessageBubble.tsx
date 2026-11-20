import React, { useState } from 'react';
import { User, Sparkles, Copy, Check, AlertCircle } from 'lucide-react';
import { ChatMessage } from '../types';
import { CitationList } from './CitationList';
import { isArabicText } from '../utils/text';

interface ChatMessageBubbleProps {
  message: ChatMessage;
}

export const ChatMessageBubble: React.FC<ChatMessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);
  const isArabic = isArabicText(message.content);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (isUser) {
    return (
      <div className="flex justify-end items-end gap-2 my-3 pl-8">
        <div className="flex flex-col items-end max-w-[85%] sm:max-w-[75%]">
          <div
            className={`px-4 py-2.5 rounded-2xl rounded-br-xs bg-stone-900 text-stone-50 text-sm leading-relaxed shadow-xs ${
              isArabic ? 'font-arabic text-right' : 'text-left'
            }`}
            dir={isArabic ? 'rtl' : 'ltr'}
          >
            {message.content}
          </div>
          <span className="text-[10px] text-stone-600 mt-1 mr-1">
            {message.timestamp}
          </span>
        </div>
        <div className="w-7 h-7 rounded-full bg-stone-200 text-stone-700 flex items-center justify-center shrink-0 mb-4">
          <User className="w-4 h-4" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start items-start gap-2.5 my-4 pr-4 sm:pr-8">
      <div className="w-8 h-8 rounded-xl bg-emerald-800 text-white flex items-center justify-center shrink-0 mt-0.5 shadow-xs">
        <Sparkles className="w-4 h-4" />
      </div>

      <div className="flex flex-col items-start max-w-[92%] sm:max-w-[85%]">
        <div className="w-full bg-white rounded-2xl rounded-tl-xs p-4 border border-stone-200/80 shadow-xs hover:border-stone-300/80 transition-all">
          {/* Ungrounded / Out-of-scope Warning Banner */}
          {message.grounded === false && (
            <div className="mb-3 px-3 py-2 rounded-lg bg-amber-50 border border-amber-200/60 text-amber-900 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-amber-700 shrink-0" />
              <span>Query outside the verified knowledge base of darglobal.com and wasalt.sa.</span>
            </div>
          )}

          {/* Assistant Content */}
          <div
            className={`text-sm text-stone-800 leading-relaxed whitespace-pre-wrap ${
              isArabic ? 'font-arabic text-right' : 'text-left'
            }`}
            dir={isArabic ? 'rtl' : 'ltr'}
          >
            {message.content}
          </div>

          {/* Citations List */}
          {message.citations && message.citations.length > 0 && (
            <CitationList citations={message.citations} />
          )}

          {/* Bottom Actions */}
          <div className="flex items-center justify-between mt-3 pt-2 border-t border-stone-100 text-[11px] text-stone-600">
            <span className="font-medium text-stone-700">
              {message.grounded !== false ? 'Grounded Answer' : 'Out-of-Scope'}
            </span>

            <div className="flex items-center gap-2">
              <button
                onClick={handleCopy}
                className="hover:text-stone-700 flex items-center gap-1 transition-colors"
                title="Copy message"
              >
                {copied ? (
                  <>
                    <Check className="w-3 h-3 text-emerald-600" />
                    <span className="text-emerald-700">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3" />
                    <span>Copy</span>
                  </>
                )}
              </button>
              <span>•</span>
              <span>{message.timestamp}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
