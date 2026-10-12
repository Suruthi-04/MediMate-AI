import React, { useState } from 'react';
import { LanguageProvider, useLanguage } from './context/LanguageContext';
import { DemoBanner } from './components/DemoBanner';
import { Navbar } from './components/Navbar';
import { Sidebar, NavPage } from './components/Sidebar';
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { UploadPage } from './pages/UploadPage';
import { ReportAnalysisPage } from './pages/ReportAnalysisPage';
import { HealthHistoryPage } from './pages/HealthHistoryPage';
import { SettingsPage } from './pages/SettingsPage';

const AppContent: React.FC = () => {
  const { t } = useLanguage();
  const [currentPage, setCurrentPage] = useState<NavPage>('landing');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedDocId, setSelectedDocId] = useState<number | null>(null);

  const handleUploadSuccess = (newDocId: number) => {
    setSelectedDocId(newDocId);
    setCurrentPage('analysis');
  };

  const handleViewReport = (docId: number) => {
    setSelectedDocId(docId);
    setCurrentPage('analysis');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col text-slate-800 font-sans selection:bg-teal-500 selection:text-white">
      {/* Top Hackathon Demo Notice */}
      <DemoBanner />

      {/* Main Top Header */}
      <Navbar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
      />

      {/* Main Shell (Sidebar + Content View) */}
      <div className="flex-1 flex w-full">
        <Sidebar
          currentPage={currentPage}
          setCurrentPage={setCurrentPage}
          isOpen={sidebarOpen}
          setIsOpen={setSidebarOpen}
          selectedDocId={selectedDocId}
        />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full transition-all">
          {currentPage === 'landing' && (
            <LandingPage
              onGetStarted={() => setCurrentPage('upload')}
              onExploreDemo={() => setCurrentPage('dashboard')}
            />
          )}

          {currentPage === 'dashboard' && (
            <DashboardPage
              onNavigateToUpload={() => setCurrentPage('upload')}
              onNavigateToAnalysis={handleViewReport}
              onNavigateToTimeline={() => setCurrentPage('history')}
            />
          )}

          {currentPage === 'upload' && (
            <UploadPage onUploadSuccess={handleUploadSuccess} />
          )}

          {currentPage === 'analysis' && (
            <ReportAnalysisPage
              documentId={selectedDocId}
              onBack={() => setCurrentPage('dashboard')}
              onSelectOtherDoc={(id) => setSelectedDocId(id)}
            />
          )}

          {currentPage === 'history' && (
            <HealthHistoryPage
              onViewReport={handleViewReport}
              onNavigateToUpload={() => setCurrentPage('upload')}
            />
          )}

          {currentPage === 'settings' && <SettingsPage />}
        </main>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 px-4 text-center text-xs text-slate-500 space-y-1">
        <p className="font-semibold text-slate-700">
          MediMate AI – Personal Health Copilot • HacXLerate 2026 Round 1
        </p>
        <p className="text-[11px] text-slate-400">
          Demonstration Prototype with Synthetic Patient Data • Not certified for clinical diagnosis. Consult a qualified medical practitioner.
        </p>
      </footer>
    </div>
  );
};

export function App() {
  return (
    <LanguageProvider>
      <AppContent />
    </LanguageProvider>
  );
}

export default App;
