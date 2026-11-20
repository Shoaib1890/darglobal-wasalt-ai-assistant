import React from 'react';
import { Building2, Sparkles, Trash2 } from 'lucide-react';
import { HealthStatus } from '../types';

interface HeaderProps {
  health: HealthStatus | null;
  isLoadingHealth: boolean;
  onClear: () => void;
  hasMessages: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  health,
  isLoadingHealth,
  onClear,
  hasMessages,
}) => {
  const isOnline = health !== null && health.status === 'healthy';

  return (
    <header className="sticky top-0 z-20 bg-[#FAF9F6]/90 backdrop-blur-md border-b border-stone-200/80 px-4 sm:px-6 py-3.5 transition-all">
      <div className="max-w-4xl mx-auto flex items-center justify-between gap-4">
        {/* Brand & Subtitle */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-800 text-white flex items-center justify-center shadow-sm shadow-emerald-900/10">
            <Building2 className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base sm:text-lg font-semibold text-stone-900 tracking-tight">
                DarGlobal <span className="text-stone-400 font-light">×</span> Wasalt
              </h1>
              <span className="hidden sm:inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200/60">
                <Sparkles className="w-3 h-3 text-emerald-600" />
                Verified AI
              </span>
            </div>
            <p className="text-xs text-stone-700 font-normal">
              Answers grounded in public information from <span className="font-medium text-stone-800">darglobal.com</span> and <span className="font-medium text-stone-800">wasalt.sa</span>
            </p>
          </div>
        </div>

        {/* Status Indicator & Controls */}
        <div className="flex items-center gap-2.5 sm:gap-3">
          {/* Health Pill */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white border border-stone-200/80 shadow-xs text-xs">
            {isLoadingHealth ? (
              <span className="w-2 h-2 rounded-full bg-stone-300 animate-pulse" />
            ) : isOnline ? (
              <>
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
                </span>
                <span className="text-stone-700 font-medium text-[11px]">Online</span>
                {health?.total_chunks ? (
                  <span className="hidden md:inline text-stone-400 text-[10px]">
                    ({health.total_chunks} chunks)
                  </span>
                ) : null}
              </>
            ) : (
              <>
                <span className="w-2 h-2 rounded-full bg-rose-500" />
                <span className="text-rose-700 font-medium text-[11px]">Connecting...</span>
              </>
            )}
          </div>

          {/* Clear Conversation */}
          {hasMessages && (
            <button
              onClick={onClear}
              title="Clear conversation"
              className="p-1.5 sm:px-2.5 sm:py-1 rounded-lg text-stone-500 hover:text-stone-800 hover:bg-stone-200/60 transition-colors flex items-center gap-1.5 text-xs font-medium border border-transparent hover:border-stone-200"
            >
              <Trash2 className="w-4 h-4" />
              <span className="hidden sm:inline">Clear</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
