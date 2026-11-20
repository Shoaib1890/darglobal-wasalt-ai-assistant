import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="text-center py-2 text-[11px] text-stone-600 border-t border-stone-200/40 bg-[#FAF9F6]">
      <p>
        Answers are based strictly on verified public information from{' '}
        <a
          href="https://www.darglobal.com/"
          target="_blank"
          rel="noopener noreferrer"
          className="underline hover:text-stone-700"
        >
          darglobal.com
        </a>{' '}
        and{' '}
        <a
          href="https://wasalt.sa/"
          target="_blank"
          rel="noopener noreferrer"
          className="underline hover:text-stone-700"
        >
          wasalt.sa
        </a>
        .
      </p>
    </footer>
  );
};
