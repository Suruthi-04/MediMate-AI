import React from 'react';
import { AlertCircle, ShieldCheck } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export const DemoBanner: React.FC = () => {
  const { t, language } = useLanguage();

  return (
    <div className="bg-slate-900 text-slate-200 text-xs py-2 px-4 border-b border-slate-800 flex flex-wrap items-center justify-between gap-2 shadow-inner">
      <div className="flex items-center gap-2">
        <span className="bg-teal-500/20 text-teal-300 font-semibold px-2 py-0.5 rounded border border-teal-500/30 text-[11px] uppercase tracking-wider">
          HacXLerate 2026
        </span>
        <span className="text-slate-300 font-medium hidden sm:inline">
          {t('challengeName')}
        </span>
        <span className="text-slate-500 hidden md:inline">•</span>
        <span className="text-amber-300 flex items-center gap-1 font-medium text-[11px]">
          <AlertCircle className="w-3.5 h-3.5 inline text-amber-400" />
          {t('demoDataBadge')}
        </span>
      </div>

      <div className="flex items-center gap-3 text-[11px] text-slate-400">
        <span className="flex items-center gap-1 text-teal-400">
          <ShieldCheck className="w-3.5 h-3.5" />
          FHIR-Inspired Schema
        </span>
        <span className="hidden sm:inline">•</span>
        <span className="bg-slate-800 px-2 py-0.5 rounded text-slate-300">
          Patient: Arun Kumar (45Y)
        </span>
      </div>
    </div>
  );
};
