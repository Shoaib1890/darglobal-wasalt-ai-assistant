import React, { useState } from 'react';
import { ExternalLink, ChevronDown, ChevronUp, ShieldCheck } from 'lucide-react';
import { Citation } from '../types';

interface CitationListProps {
  citations: Citation[];
}

export const CitationList: React.FC<CitationListProps> = ({ citations }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-3 pt-2.5 border-t border-stone-200/70">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-1.5 text-xs font-medium text-emerald-800 hover:text-emerald-900 transition-colors py-1 group"
      >
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-700" />
        <span>
          {citations.length} Verified {citations.length === 1 ? 'Source' : 'Sources'}
        </span>
        {isExpanded ? (
          <ChevronUp className="w-3.5 h-3.5 text-stone-400 group-hover:text-stone-600" />
        ) : (
          <ChevronDown className="w-3.5 h-3.5 text-stone-400 group-hover:text-stone-600" />
        )}
      </button>

      {isExpanded && (
        <div className="mt-2 space-y-2">
          {citations.map((c, i) => (
            <div
              key={`${c.chunk_id}-${i}`}
              className="bg-stone-50 rounded-lg p-2.5 text-xs border border-stone-200/60 transition-colors hover:border-emerald-200"
            >
              <div className="flex items-center justify-between gap-2 mb-1">
                <span className="font-semibold text-stone-800 inline-flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
                  {c.domain}
                </span>
                <a
                  href={c.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-emerald-700 hover:text-emerald-800 hover:underline flex items-center gap-1 text-[11px] font-medium"
                >
                  <span>Visit website</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              <div className="text-stone-600 text-[11px] font-medium mb-1">
                Section: {c.section}
              </div>
              {c.quote && (
                <p className="text-stone-500 text-[11px] leading-relaxed italic bg-white/70 p-1.5 rounded border border-stone-100 line-clamp-3">
                  "{c.quote}"
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
