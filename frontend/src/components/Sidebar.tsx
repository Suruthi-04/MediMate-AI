import React from 'react';
import {
  Home,
  LayoutDashboard,
  UploadCloud,
  FileText,
  Clock,
  Settings,
  ChevronRight,
  Shield,
  PlusCircle
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export type NavPage = 'landing' | 'dashboard' | 'upload' | 'analysis' | 'history' | 'settings';

interface SidebarProps {
  currentPage: NavPage;
  setCurrentPage: (page: NavPage) => void;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  selectedDocId?: number | null;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentPage,
  setCurrentPage,
  isOpen,
  setIsOpen,
  selectedDocId
}) => {
  const { t } = useLanguage();

  const navItems = [
    { id: 'landing', label: t('navHome'), icon: Home },
    { id: 'dashboard', label: t('navDashboard'), icon: LayoutDashboard },
    { id: 'upload', label: t('navUpload'), icon: UploadCloud },
    { id: 'analysis', label: t('navReportAnalysis'), icon: FileText, badge: selectedDocId ? 'Report' : undefined },
    { id: 'history', label: t('navHistory'), icon: Clock },
    { id: 'settings', label: t('navSettings'), icon: Settings },
  ];

  const handleNavClick = (pageId: string) => {
    setCurrentPage(pageId as NavPage);
    setIsOpen(false);
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-white border-r border-slate-200/90 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:static lg:z-10`}
      >
        {/* Brand Section in sidebar */}
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-teal-600 text-white flex items-center justify-center font-bold text-sm shadow-xs">
              M
            </div>
            <div>
              <span className="font-bold text-sm text-slate-900 block leading-tight">
                {t('appName')}
              </span>
              <span className="text-[10px] text-teal-700 font-medium">Personal Copilot</span>
            </div>
          </div>
        </div>

        {/* Quick Upload CTA */}
        <div className="p-3">
          <button
            onClick={() => handleNavClick('upload')}
            className="w-full flex items-center justify-center gap-2 py-2.5 px-3 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-semibold shadow-sm hover:shadow transition-all cursor-pointer"
          >
            <PlusCircle className="w-4 h-4" />
            <span>{t('uploadDocument')}</span>
          </button>
        </div>

        {/* Navigation list */}
        <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                  isActive
                    ? 'bg-teal-50 text-teal-900 font-semibold shadow-xs border border-teal-200/50'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`w-4 h-4 transition-colors ${
                      isActive ? 'text-teal-600' : 'text-slate-400'
                    }`}
                  />
                  <span>{item.label}</span>
                </div>

                {item.badge ? (
                  <span className="text-[10px] bg-teal-100 text-teal-800 px-2 py-0.5 rounded-full font-medium">
                    {item.badge}
                  </span>
                ) : (
                  isActive && <ChevronRight className="w-3.5 h-3.5 text-teal-600" />
                )}
              </button>
            );
          })}
        </nav>

        {/* Bottom Safety card */}
        <div className="p-3 border-t border-slate-100 bg-slate-50/60 m-2 rounded-xl text-xs">
          <div className="flex items-center gap-1.5 text-slate-700 font-semibold mb-1 text-[11px]">
            <Shield className="w-3.5 h-3.5 text-teal-600" />
            <span>Health Privacy & Safety</span>
          </div>
          <p className="text-[11px] text-slate-500 leading-normal">
            Non-diagnostic AI assistant. All clinical parameters stay in your local workspace.
          </p>
        </div>
      </aside>
    </>
  );
};
