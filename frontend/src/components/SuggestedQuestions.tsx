import React from 'react';
import { Compass, Building, Landmark, GraduationCap, Gavel } from 'lucide-react';

interface SuggestedQuestionsProps {
  onSelect: (question: string) => void;
}

const QUESTIONS = [
  {
    icon: Building,
    title: 'What is DAR Global?',
    desc: 'Company background & founder Alidar Utemuratov',
    domain: 'darglobal.com',
  },
  {
    icon: GraduationCap,
    title: 'What are the different projects under the DAR ecosystem?',
    desc: 'Naiza, DAR U, Darlean, Dossym, TNS+ and QAZCODE',
    domain: 'darglobal.com',
  },
  {
    icon: Landmark,
    title: 'What is Wasalt?',
    desc: 'Saudi AI-powered real estate marketplace & REGA licensing',
    domain: 'wasalt.sa',
  },
  {
    icon: Gavel,
    title: 'How does the Wasalt auction process work?',
    desc: 'Digital real estate bidding and asset auctions',
    domain: 'wasalt.sa',
  },
  {
    icon: Compass,
    title: 'What services does Wasalt provide?',
    desc: 'Property sales, rentals, brokerage & commercial listings',
    domain: 'wasalt.sa',
  },
  {
    icon: Landmark,
    title: 'ما هي منصة وصلت؟',
    desc: 'المنصة العقارية الرائدة وتراخيص الهيئة العامة للعقار',
    domain: 'wasalt.sa',
    isArabic: true,
  },
];

export const SuggestedQuestions: React.FC<SuggestedQuestionsProps> = ({ onSelect }) => {
  return (
    <div className="w-full max-w-2xl mx-auto my-6 px-4">
      <div className="text-center mb-6">
        <h2 className="text-xl sm:text-2xl font-bold text-stone-900 tracking-tight mb-2">
          Explore Public Knowledge
        </h2>
        <p className="text-sm text-stone-700 max-w-md mx-auto">
          Ask any question regarding DAR Ecosystem ventures or Wasalt's Saudi real estate platform and licensing.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {QUESTIONS.map((q, idx) => {
          const Icon = q.icon;
          return (
            <button
              key={idx}
              onClick={() => onSelect(q.title)}
              className="group text-left p-3.5 rounded-xl bg-white border border-stone-200/80 shadow-xs hover:border-emerald-600/40 hover:shadow-sm hover:shadow-emerald-900/5 transition-all flex items-start gap-3"
            >
              <div className="w-8 h-8 rounded-lg bg-stone-100 text-stone-700 flex items-center justify-center shrink-0 group-hover:bg-emerald-50 group-hover:text-emerald-700 transition-colors">
                <Icon className="w-4 h-4" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-1 mb-0.5">
                  <span
                    className={`text-xs font-semibold text-stone-800 group-hover:text-emerald-800 transition-colors truncate ${
                      q.isArabic ? 'font-arabic text-right' : ''
                    }`}
                    dir={q.isArabic ? 'rtl' : 'ltr'}
                  >
                    {q.title}
                  </span>
                </div>
                <p
                  className={`text-[11px] text-stone-600 line-clamp-1 ${
                    q.isArabic ? 'text-right' : ''
                  }`}
                  dir={q.isArabic ? 'rtl' : 'ltr'}
                >
                  {q.desc}
                </p>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
