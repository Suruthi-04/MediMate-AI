import React from 'react';
import { Activity, Globe, Menu, X, Sparkles, User } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

interface NavbarProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  activeAiProvider?: string;
  isDemoMode?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  sidebarOpen,
  setSidebarOpen,
  activeAiProvider = 'MediMate Clinical Engine',
  isDemoMode = true,
}) => {
  const { language, toggleLanguage, t } = useLanguage();

  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-4 lg:px-6 py-3 transition-all">
      <div className="flex items-center justify-between gap-4">
        {/* Left: Mobile hamburger & Logo */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
            aria-label="Toggle navigation"
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>

          <div className="flex items-center gap-2.5 cursor-pointer">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-teal-600 to-teal-500 flex items-center justify-center text-white shadow-md shadow-teal-500/20">
              <Activity className="w-5 h-5 stroke-[2.2]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg text-slate-900 tracking-tight">
                  {t('appName')}
                </span>
                <span className="hidden sm:inline-block text-[11px] font-semibold bg-teal-50 text-teal-700 px-2 py-0.5 rounded-full border border-teal-200/60">
                  v1.0
                </span>
              </div>
              <p className="text-xs text-slate-500 -mt-0.5 hidden sm:block">
                {t('appSubtitle')}
              </p>
            </div>
          </div>
        </div>

        {/* Right: AI Engine status, Language Switcher, Patient Chip */}
        <div className="flex items-center gap-2.5 sm:gap-3">
          {/* AI Status Badge */}
          <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
            <Sparkles className="w-3.5 h-3.5 text-teal-600 animate-pulse" />
            <span className="max-w-[180px] truncate">{activeAiProvider}</span>
            {isDemoMode && (
              <span className="bg-amber-100 text-amber-800 text-[10px] px-1.5 py-0.2 rounded font-bold">
                DEMO
              </span>
            )}
          </div>

          {/* Language Switcher Toggle */}
          <button
            onClick={toggleLanguage}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-teal-200 bg-teal-50/70 hover:bg-teal-100/70 text-teal-800 text-xs font-semibold transition-all shadow-2xs cursor-pointer"
            title="Switch Language / மொழியை மாற்றவும்"
          >
            <Globe className="w-3.5 h-3.5 text-teal-700" />
            <span>{language === 'en' ? 'தமிழ் (Tamil)' : 'English'}</span>
          </button>

          {/* Patient Profile Chip */}
          <div className="hidden sm:flex items-center gap-2 pl-2 border-l border-slate-200">
            <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center font-bold text-xs shadow-xs">
              <User className="w-4 h-4" />
            </div>
            <div className="text-left text-xs leading-tight hidden lg:block">
              <span className="font-semibold text-slate-800 block">Arun Kumar</span>
              <span className="text-[10px] text-slate-500">ID: PAT-HACX-2026</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
