import React, { useState, useEffect } from 'react';
import {
  Clock,
  Calendar,
  Building,
  FileText,
  AlertTriangle,
  Trash2,
  Eye,
  Filter,
  ArrowUpDown,
  RefreshCw,
  Plus
} from 'lucide-react';
import { TimelineItem } from '../types';
import { api } from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import { MedicalDisclaimer } from '../components/MedicalDisclaimer';

interface HealthHistoryPageProps {
  onViewReport: (docId: number) => void;
  onNavigateToUpload: () => void;
}

export const HealthHistoryPage: React.FC<HealthHistoryPageProps> = ({
  onViewReport,
  onNavigateToUpload,
}) => {
  const { t } = useLanguage();
  const [timeline, setTimeline] = useState<TimelineItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDocType, setSelectedDocType] = useState('All');
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc');

  const loadTimeline = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getTimeline(selectedDocType, sortOrder);
      setTimeline(data.timeline);
    } catch (err: any) {
      setError(err.message || 'Failed to load health history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTimeline();
  }, [selectedDocType, sortOrder]);

  const handleDelete = async (docId: number, title: string) => {
    if (!confirm(`Are you sure you want to delete '${title}'? This will remove all associated test observations and conditions.`)) {
      return;
    }
    try {
      await api.deleteDocument(docId);
      setTimeline((prev) => prev.filter((item) => item.id !== docId));
    } catch (err: any) {
      alert(err.message || 'Failed to delete record');
    }
  };

  const docTypes = ['All', 'Complete Blood Count', 'Lipid Profile', 'Diabetic Panel', 'Prescription', 'Discharge Summary'];

  return (
    <div className="space-y-6">
      {/* Header and Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">
              {t('navHistory')}
            </h1>
            <span className="text-[11px] font-bold bg-teal-50 text-teal-700 px-2 py-0.5 rounded-full border border-teal-200">
              {timeline.length} Records
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Chronological health timeline stored in local FHIR-inspired SQLite database.
          </p>
        </div>

        <button
          onClick={onNavigateToUpload}
          className="flex items-center gap-1.5 px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-bold shadow-xs transition-colors cursor-pointer self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>{t('uploadDocument')}</span>
        </button>
      </div>

      <MedicalDisclaimer compact={true} />

      {/* Filter and Sorting Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200/90 flex flex-wrap items-center justify-between gap-3 shadow-xs">
        {/* Document Type Pills */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-xs font-semibold text-slate-500 mr-1 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" /> Filter:
          </span>
          {docTypes.map((type) => (
            <button
              key={type}
              onClick={() => setSelectedDocType(type)}
              className={`px-3 py-1 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                selectedDocType === type
                  ? 'bg-teal-600 text-white shadow-xs'
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
              }`}
            >
              {type}
            </button>
          ))}
        </div>

        {/* Sort Order Toggle */}
        <button
          onClick={() => setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc')}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer"
        >
          <ArrowUpDown className="w-3.5 h-3.5 text-teal-600" />
          <span>{sortOrder === 'desc' ? 'Newest First' : 'Oldest First'}</span>
        </button>
      </div>

      {/* Timeline Stream */}
      {loading ? (
        <div className="py-16 text-center space-y-2">
          <RefreshCw className="w-6 h-6 text-teal-600 animate-spin mx-auto" />
          <p className="text-xs text-slate-500">Loading timeline records...</p>
        </div>
      ) : timeline.length === 0 ? (
        <div className="p-12 text-center bg-white rounded-2xl border border-slate-200 space-y-3">
          <Clock className="w-8 h-8 text-slate-300 mx-auto" />
          <h3 className="font-bold text-slate-800 text-sm">No medical records match this filter</h3>
          <p className="text-xs text-slate-500">Try changing the filter or upload a new record.</p>
        </div>
      ) : (
        <div className="relative pl-6 sm:pl-8 space-y-6 before:absolute before:left-3 sm:before:left-4 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-200">
          {timeline.map((item, idx) => {
            const hasAbnormal = item.abnormal_observations > 0;
            return (
              <div key={item.id} className="relative group">
                {/* Timeline node dot */}
                <div
                  className={`absolute -left-6 sm:-left-8 top-4 w-6 h-6 rounded-full border-4 border-white shadow-xs flex items-center justify-center ${
                    hasAbnormal ? 'bg-amber-500' : 'bg-teal-600'
                  }`}
                />

                {/* Card Container */}
                <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs hover:shadow-md transition-all">
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                    <div className="space-y-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-xs font-bold text-teal-800 bg-teal-50 px-2.5 py-0.5 rounded-full border border-teal-200/60">
                          {item.doc_type}
                        </span>
                        <span className="flex items-center gap-1 text-xs text-slate-500 font-semibold">
                          <Calendar className="w-3.5 h-3.5 text-slate-400" />
                          {item.report_date}
                        </span>
                      </div>

                      <h3 className="font-bold text-base text-slate-900">
                        {item.title}
                      </h3>

                      {item.facility_name && (
                        <p className="text-xs text-slate-500 flex items-center gap-1">
                          <Building className="w-3.5 h-3.5 text-slate-400" />
                          <span>{item.facility_name}</span>
                          {item.doctor_name && <span>• {item.doctor_name}</span>}
                        </p>
                      )}
                    </div>

                    {/* Action Buttons */}
                    <div className="flex items-center gap-2 self-start sm:self-center">
                      <button
                        onClick={() => onViewReport(item.id)}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-teal-50 hover:bg-teal-100 text-teal-800 rounded-xl text-xs font-bold transition-colors cursor-pointer"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>{t('viewReport')}</span>
                      </button>

                      <button
                        onClick={() => handleDelete(item.id, item.title)}
                        className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-colors cursor-pointer"
                        title={t('delete')}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Summary badges row */}
                  <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap items-center gap-2 text-xs">
                    <span className="text-slate-600 font-medium">
                      <strong>{item.total_observations}</strong> Lab parameters
                    </span>

                    {hasAbnormal ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 font-semibold border border-amber-200">
                        <AlertTriangle className="w-3 h-3 text-amber-600" />
                        {item.abnormal_observations} Outside Range
                      </span>
                    ) : (
                      <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full font-medium">
                        All in range
                      </span>
                    )}

                    {item.medications_count > 0 && (
                      <span className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full font-medium">
                        {item.medications_count} Prescriptions
                      </span>
                    )}

                    {item.conditions.length > 0 && (
                      <span className="bg-teal-50 text-teal-800 px-2 py-0.5 rounded-full font-medium truncate max-w-xs">
                        Conditions: {item.conditions.join(', ')}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
