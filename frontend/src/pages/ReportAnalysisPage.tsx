import React, { useState, useEffect } from 'react';
import {
  FileText,
  Calendar,
  Building,
  User,
  ArrowLeft,
  RefreshCw,
  FileCheck,
  Pill,
  Activity,
  AlertTriangle,
  Plus,
  Trash2
} from 'lucide-react';
import { DocumentReference, Observation } from '../types';
import { api } from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import { AIExplanationCard } from '../components/AIExplanationCard';
import { LabResultTable } from '../components/LabResultTable';
import { RawTextViewerModal } from '../components/RawTextViewerModal';
import { MedicalDisclaimer } from '../components/MedicalDisclaimer';

interface ReportAnalysisPageProps {
  documentId: number | null;
  onBack: () => void;
  onSelectOtherDoc: (id: number) => void;
}

export const ReportAnalysisPage: React.FC<ReportAnalysisPageProps> = ({
  documentId,
  onBack,
  onSelectOtherDoc,
}) => {
  const { t } = useLanguage();
  const [doc, setDoc] = useState<DocumentReference | null>(null);
  const [allDocs, setAllDocs] = useState<DocumentReference[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showRawModal, setShowRawModal] = useState(false);

  const loadDocument = async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getDocumentById(id);
      setDoc(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load report');
    } finally {
      setLoading(false);
    }
  };

  const loadAllDocs = async () => {
    try {
      const list = await api.getDocuments();
      setAllDocs(list);
      if (!documentId && list.length > 0) {
        loadDocument(list[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadAllDocs();
  }, []);

  useEffect(() => {
    if (documentId) {
      loadDocument(documentId);
    }
  }, [documentId]);

  const handleUpdateObservation = async (obsId: number, updated: Partial<Observation>) => {
    if (!doc) return;
    try {
      const updatedObs = await api.updateObservation(obsId, updated);
      // Update local state
      setDoc({
        ...doc,
        observations: doc.observations.map((o) => (o.id === obsId ? updatedObs : o)),
      });
      // Auto regenerate AI summary based on corrected values
      const res = await api.regenerateSummary(doc.id);
      setDoc((prev) =>
        prev
          ? {
              ...prev,
              summary_en: res.summary_en,
              summary_ta: res.summary_ta,
              key_findings_json: JSON.stringify(res.key_findings),
              doctor_questions_json: JSON.stringify(res.doctor_questions),
            }
          : null
      );
    } catch (err: any) {
      alert(err.message || 'Failed to update observation');
    }
  };

  const handleDeleteObservation = async (obsId: number) => {
    if (!doc || !confirm('Are you sure you want to remove this observation?')) return;
    try {
      await api.deleteObservation(obsId);
      setDoc({
        ...doc,
        observations: doc.observations.filter((o) => o.id !== obsId),
      });
      await api.regenerateSummary(doc.id);
    } catch (err: any) {
      alert(err.message || 'Failed to delete');
    }
  };

  const handleRegenerateSummary = async () => {
    if (!doc) return;
    try {
      const res = await api.regenerateSummary(doc.id);
      setDoc({
        ...doc,
        summary_en: res.summary_en,
        summary_ta: res.summary_ta,
        key_findings_json: JSON.stringify(res.key_findings),
        doctor_questions_json: JSON.stringify(res.doctor_questions),
        ai_model: res.ai_model,
        is_demo_mode: res.is_demo_mode,
      });
    } catch (err: any) {
      alert(err.message || 'Failed to regenerate AI summary');
    }
  };

  if (loading) {
    return (
      <div className="py-20 text-center space-y-3">
        <RefreshCw className="w-8 h-8 text-teal-600 animate-spin mx-auto" />
        <p className="text-sm font-semibold text-slate-700">Loading Report Analysis...</p>
      </div>
    );
  }

  if (error || !doc) {
    return (
      <div className="p-8 text-center bg-white rounded-2xl border border-slate-200 space-y-4">
        <AlertTriangle className="w-10 h-10 text-amber-500 mx-auto" />
        <h3 className="font-bold text-slate-900 text-base">
          {error || 'No document selected'}
        </h3>
        <p className="text-xs text-slate-500">
          Please select an existing report from the health timeline or upload a new record.
        </p>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-teal-600 text-white rounded-xl text-xs font-semibold"
        >
          {t('backToDashboard')}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Navigation & Selector Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <button
          onClick={onBack}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{t('backToDashboard')}</span>
        </button>

        {/* Document Switcher Dropdown if multiple docs exist */}
        {allDocs.length > 1 && (
          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-500 font-medium">Switch Report:</span>
            <select
              value={doc.id}
              onChange={(e) => onSelectOtherDoc(Number(e.target.value))}
              className="bg-white border border-slate-300 rounded-xl px-3 py-1.5 text-xs text-slate-800 font-semibold focus:outline-none focus:ring-2 focus:ring-teal-500/20"
            >
              {allDocs.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.title} ({d.report_date})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Document Header Card */}
      <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-teal-100 text-teal-800 uppercase tracking-wide">
                {doc.doc_type}
              </span>
              <span className="text-xs font-medium text-slate-500">
                File: {doc.file_name}
              </span>
            </div>
            <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">
              {doc.title}
            </h1>
          </div>

          {/* Metadata Badges */}
          <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600">
            <div className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl">
              <Calendar className="w-3.5 h-3.5 text-teal-600" />
              <span>{doc.report_date || 'Date not recorded'}</span>
            </div>

            {doc.facility_name && (
              <div className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl">
                <Building className="w-3.5 h-3.5 text-teal-600" />
                <span>{doc.facility_name}</span>
              </div>
            )}

            {doc.doctor_name && (
              <div className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl">
                <User className="w-3.5 h-3.5 text-teal-600" />
                <span>{doc.doctor_name}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Section 1: AI Health Summary (English & Tamil with Questions for Doctor) */}
      <AIExplanationCard
        summaryEn={doc.summary_en}
        summaryTa={doc.summary_ta}
        keyFindingsJson={doc.key_findings_json}
        doctorQuestionsJson={doc.doctor_questions_json}
        aiModel={doc.ai_model}
        isDemoMode={doc.is_demo_mode}
        onRegenerate={handleRegenerateSummary}
        onViewRawText={() => setShowRawModal(true)}
      />

      {/* Section 2: Structured Extracted Lab Results Table */}
      <LabResultTable
        observations={doc.observations}
        onUpdateObservation={handleUpdateObservation}
        onDeleteObservation={handleDeleteObservation}
      />

      {/* Section 3: Extracted Prescriptions and Diagnoses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Identified Medications */}
        <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs">
          <div className="flex items-center gap-2 mb-3">
            <div className="p-1.5 rounded-lg bg-teal-50 text-teal-700">
              <Pill className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-sm text-slate-900">
              {t('medicationsTitle')} ({doc.medications.length})
            </h3>
          </div>

          {doc.medications.length === 0 ? (
            <p className="text-xs text-slate-400 italic">No prescription medications detected in this document.</p>
          ) : (
            <div className="space-y-2.5">
              {doc.medications.map((med) => (
                <div
                  key={med.id}
                  className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-xs flex items-start justify-between"
                >
                  <div>
                    <span className="font-bold text-slate-900 block">{med.medication_name}</span>
                    <span className="text-[11px] text-slate-600">{med.dosage_instruction}</span>
                  </div>
                  <span className="text-[10px] font-semibold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full">
                    {med.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Identified Conditions / Diagnoses */}
        <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs">
          <div className="flex items-center gap-2 mb-3">
            <div className="p-1.5 rounded-lg bg-teal-50 text-teal-700">
              <Activity className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-sm text-slate-900">
              {t('conditionsTitle')} ({doc.conditions.length})
            </h3>
          </div>

          {doc.conditions.length === 0 ? (
            <p className="text-xs text-slate-400 italic">No specific clinical conditions flagged.</p>
          ) : (
            <div className="space-y-2.5">
              {doc.conditions.map((cond) => (
                <div
                  key={cond.id}
                  className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-xs flex items-start justify-between"
                >
                  <div>
                    <span className="font-bold text-slate-900 block">{cond.display_name}</span>
                    <span className="text-[11px] text-slate-500">{cond.notes || 'Recorded in diagnostic report'}</span>
                  </div>
                  <span className="text-[10px] font-semibold bg-teal-100 text-teal-800 px-2 py-0.5 rounded-full">
                    {cond.clinical_status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Medical Disclaimer */}
      <MedicalDisclaimer />

      {/* Raw Text Viewer Modal */}
      <RawTextViewerModal
        isOpen={showRawModal}
        onClose={() => setShowRawModal(false)}
        title={doc.title}
        rawText={doc.raw_extracted_text || ''}
      />
    </div>
  );
};
