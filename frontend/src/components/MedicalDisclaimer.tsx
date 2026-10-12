import React, { useState } from 'react';
import { AlertTriangle, ChevronDown, ChevronUp, ShieldAlert } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export const MedicalDisclaimer: React.FC<{ compact?: boolean }> = ({ compact = false }) => {
  const { t, language } = useLanguage();
  const [expanded, setExpanded] = useState(!compact);

  return (
    <div className="bg-amber-50/90 border border-amber-200/90 rounded-xl p-4 my-3 text-amber-950 transition-all shadow-xs">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2.5">
          <div className="p-1.5 bg-amber-100 rounded-lg text-amber-700 mt-0.5 shrink-0">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="font-semibold text-sm text-amber-900 tracking-tight">
                {t('disclaimerTitle')}
              </h4>
              <span className="text-[10px] bg-amber-200/80 text-amber-800 font-medium px-2 py-0.5 rounded-full uppercase">
                Educational Copilot
              </span>
            </div>
            
            <p className="text-xs text-amber-800/90 mt-1 leading-relaxed">
              {expanded ? t('disclaimerFull') : t('disclaimerShort')}
            </p>
          </div>
        </div>

        {compact && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-amber-700 hover:text-amber-900 p-1 rounded-md hover:bg-amber-100/50 transition-colors shrink-0"
            aria-label="Toggle disclaimer details"
          >
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        )}
      </div>
    </div>
  );
};
