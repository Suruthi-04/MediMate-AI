import React, { useState, useEffect } from 'react';
import {
  FileText,
  Activity,
  AlertTriangle,
  Pill,
  UploadCloud,
  Clock,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Calendar,
  Building,
  RefreshCw
} from 'lucide-react';
import { DashboardStats, DocumentReference, Observation } from '../types';
import { api } from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import { MetricCard } from '../components/MetricCard';
import { MedicalDisclaimer } from '../components/MedicalDisclaimer';

interface DashboardPageProps {
  onNavigateToUpload: () => void;
  onNavigateToAnalysis: (docId: number) => void;
  onNavigateToTimeline: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  onNavigateToUpload,
  onNavigateToAnalysis,
  onNavigateToTimeline,
}) => {
  const { t, language } = useLanguage();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSampleLoading, setIsSampleLoading] = useState(false);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard statistics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleQuickSample = async (sampleType: 'cbc' | 'lipid') => {
    setIsSampleLoading(true);
    try {
      const newDoc = await api.loadSampleDocument(sampleType);
      await loadData();
      onNavigateToAnalysis(newDoc.id);
    } catch (err: any) {
      alert(err.message || 'Failed to load sample');
    } finally {
      setIsSampleLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="py-16 text-center space-y-3">
        <RefreshCw className="w-8 h-8 text-teal-600 animate-spin mx-auto" />
        <p className="text-sm font-semibold text-slate-700">Loading MediMate Dashboard...</p>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-2xl text-red-700 text-sm space-y-3">
        <p className="font-bold">Error loading dashboard: {error}</p>
        <button
          onClick={loadData}
          className="px-4 py-2 bg-red-600 text-white rounded-xl text-xs font-semibold cursor-pointer"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome & Quick Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200/90 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">
              Patient Health Overview
            </h1>
            <span className="text-[11px] font-bold bg-teal-50 text-teal-700 px-2 py-0.5 rounded-full border border-teal-200">
              Active Record
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Patient: <span className="font-semibold text-slate-800">Arun Kumar</span> (45 Y, Male, O+) • Record ID: PAT-HACX-2026
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => handleQuickSample('cbc')}
            disabled={isSampleLoading}
            className="flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-xl text-xs font-semibold transition-colors cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5 text-teal-600" />
            <span>Load Sample CBC Report</span>
          </button>

          <button
            onClick={onNavigateToUpload}
            className="flex items-center gap-1.5 px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-bold shadow-xs transition-colors cursor-pointer"
          >
            <UploadCloud className="w-4 h-4" />
            <span>{t('uploadDocument')}</span>
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title={t('totalReports')}
          value={stats.total_reports}
          subtitle="Processed medical documents"
          icon={FileText}
          variant="teal"
          onClick={onNavigateToTimeline}
        />
        <MetricCard
          title={t('totalTests')}
          value={stats.total_tests}
          subtitle="Extracted lab parameters"
          icon={Activity}
          variant="navy"
        />
        <MetricCard
          title={t('abnormalTests')}
          value={stats.abnormal_tests_count}
          subtitle="Outside biological range"
          icon={AlertTriangle}
          variant="amber"
          badge={stats.abnormal_tests_count > 0 ? "Review Needed" : undefined}
        />
        <MetricCard
          title={t('activeMeds')}
          value={stats.active_medications_count}
          subtitle="Prescribed active therapies"
          icon={Pill}
          variant="slate"
        />
      </div>

      {/* Medical Disclaimer Banner */}
      <MedicalDisclaimer compact={true} />

      {/* Two Column Grid: Recent Documents & Abnormal Highlights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2/3): Recent Uploaded Records */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200/90 overflow-hidden shadow-xs">
          <div className="p-4 sm:p-5 bg-slate-50/70 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h2 className="font-bold text-slate-900 text-sm sm:text-base">
                {t('recentUploads')}
              </h2>
              <p className="text-xs text-slate-500">
                Latest records ingested and analyzed by MediMate AI
              </p>
            </div>
            <button
              onClick={onNavigateToTimeline}
              className="text-xs font-semibold text-teal-700 hover:text-teal-900 flex items-center gap-1 cursor-pointer"
            >
              <span>View All Timeline</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="divide-y divide-slate-100">
            {stats.recent_documents.length === 0 ? (
              <div className="p-8 text-center space-y-3">
                <FileText className="w-8 h-8 text-slate-300 mx-auto" />
                <p className="text-xs text-slate-500 italic">No medical documents uploaded yet.</p>
                <button
                  onClick={onNavigateToUpload}
                  className="px-4 py-2 bg-teal-600 text-white rounded-xl text-xs font-semibold"
                >
                  Upload First Record
                </button>
              </div>
            ) : (
              stats.recent_documents.map((doc) => {
                const abnormalCount = doc.observations.filter(
                  (o) => o.interpretation !== 'Normal'
                ).length;

                return (
                  <div
                    key={doc.id}
                    onClick={() => onNavigateToAnalysis(doc.id)}
                    className="p-4 hover:bg-slate-50/80 transition-colors flex items-center justify-between gap-4 cursor-pointer"
                  >
                    <div className="flex items-start gap-3">
                      <div className="p-2.5 rounded-xl bg-teal-50 text-teal-700 shrink-0 mt-0.5">
                        <FileText className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-bold text-xs sm:text-sm text-slate-900">
                            {doc.title}
                          </h3>
                          <span className="text-[10px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full font-medium">
                            {doc.doc_type}
                          </span>
                        </div>

                        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-slate-500 mt-1">
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3 text-slate-400" />
                            {doc.report_date || 'Date not recorded'}
                          </span>
                          {doc.facility_name && (
                            <span className="flex items-center gap-1">
                              <Building className="w-3 h-3 text-slate-400" />
                              {doc.facility_name}
                            </span>
                          )}
                          <span className="text-slate-400">•</span>
                          <span>{doc.observations.length} tests</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      {abnormalCount > 0 ? (
                        <span className="text-[11px] font-semibold bg-amber-100 text-amber-800 px-2.5 py-1 rounded-full border border-amber-200">
                          {abnormalCount} Out of Range
                        </span>
                      ) : (
                        <span className="text-[11px] font-semibold bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded-full border border-emerald-200">
                          All Normal
                        </span>
                      )}
                      <ArrowRight className="w-4 h-4 text-slate-400" />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Column (1/3): Key Clinical Highlights */}
        <div className="bg-white rounded-2xl border border-slate-200/90 overflow-hidden shadow-xs flex flex-col">
          <div className="p-4 sm:p-5 bg-slate-50/70 border-b border-slate-100">
            <h2 className="font-bold text-slate-900 text-sm sm:text-base flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              <span>{t('recentAbnormalAlerts')}</span>
            </h2>
            <p className="text-xs text-slate-500">
              Parameters to discuss with your healthcare provider
            </p>
          </div>

          <div className="p-4 space-y-3 flex-1 overflow-y-auto">
            {stats.recent_abnormal_observations.length === 0 ? (
              <div className="p-6 text-center text-slate-400 text-xs italic">
                <CheckCircle2 className="w-6 h-6 text-emerald-500 mx-auto mb-2" />
                No abnormal test results detected in recent reports.
              </div>
            ) : (
              stats.recent_abnormal_observations.map((obs) => (
                <div
                  key={obs.id}
                  onClick={() => onNavigateToAnalysis(obs.document_id)}
                  className="p-3 rounded-xl border border-amber-200/80 bg-amber-50/40 hover:bg-amber-50 text-xs transition-colors cursor-pointer"
                >
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="font-bold text-slate-900">
                      {obs.display_name}
                    </span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-200 text-amber-900 uppercase">
                      {obs.interpretation}
                    </span>
                  </div>

                  <div className="flex items-baseline justify-between text-[11px] text-slate-600">
                    <div>
                      Observed: <strong className="text-slate-900">{obs.value_string} {obs.unit || ''}</strong>
                    </div>
                    <div className="text-[10px] text-slate-500">
                      Ref: {obs.reference_range_text || 'Standard'}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
