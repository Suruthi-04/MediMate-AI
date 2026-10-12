import React, { useState } from 'react';
import { Edit2, Trash2, CheckCircle2, AlertCircle, AlertTriangle } from 'lucide-react';
import { Observation } from '../types';
import { useLanguage } from '../context/LanguageContext';
import { LabResultEditModal } from './LabResultEditModal';

interface LabResultTableProps {
  observations: Observation[];
  onUpdateObservation: (id: number, updated: Partial<Observation>) => Promise<void>;
  onDeleteObservation?: (id: number) => Promise<void>;
}

export const LabResultTable: React.FC<LabResultTableProps> = ({
  observations,
  onUpdateObservation,
  onDeleteObservation,
}) => {
  const { t } = useLanguage();
  const [editingObs, setEditingObs] = useState<Observation | null>(null);

  const getInterpretationBadge = (inter: string) => {
    switch (inter) {
      case 'High':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200">
            <AlertTriangle className="w-3 h-3" />
            {t('high')}
          </span>
        );
      case 'Low':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200">
            <AlertTriangle className="w-3 h-3" />
            {t('low')}
          </span>
        );
      case 'Critical':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-200">
            <AlertCircle className="w-3 h-3 text-rose-600" />
            {t('critical')}
          </span>
        );
      case 'Normal':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3 h-3 text-emerald-600" />
            {t('normal')}
          </span>
        );
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 overflow-hidden shadow-xs">
      <div className="p-4 bg-slate-50/60 border-b border-slate-100 flex items-center justify-between">
        <div>
          <h3 className="font-bold text-slate-900 text-sm">
            {t('labResultsTable')} ({observations.length})
          </h3>
          <p className="text-xs text-slate-500">
            Structured biological parameters parsed from report
          </p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50/80 text-[11px] font-semibold text-slate-600 border-b border-slate-200 uppercase tracking-wider">
              <th className="py-3 px-4">{t('testName')}</th>
              <th className="py-3 px-4">{t('observedValue')}</th>
              <th className="py-3 px-4">{t('referenceRange')}</th>
              <th className="py-3 px-4">{t('status')}</th>
              <th className="py-3 px-4 text-right">{t('actions')}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-xs">
            {observations.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-8 text-center text-slate-400 italic">
                  No laboratory tests identified in this document.
                </td>
              </tr>
            ) : (
              observations.map((obs) => {
                const isAbnormal = obs.interpretation !== 'Normal';
                return (
                  <tr
                    key={obs.id}
                    className={`hover:bg-slate-50/60 transition-colors ${
                      isAbnormal ? 'bg-amber-50/20' : ''
                    }`}
                  >
                    <td className="py-3 px-4 font-semibold text-slate-900">
                      <div className="flex items-center gap-2">
                        <span>{obs.display_name}</span>
                        {obs.user_corrected && (
                          <span className="text-[10px] bg-teal-50 text-teal-700 font-medium px-1.5 py-0.2 rounded border border-teal-200">
                            {t('verified')}
                          </span>
                        )}
                        {obs.is_uncertain && (
                          <span className="text-[10px] bg-amber-100 text-amber-800 font-medium px-1.5 py-0.2 rounded">
                            {t('uncertain')}
                          </span>
                        )}
                      </div>
                      {obs.notes && (
                        <span className="text-[11px] text-slate-400 block font-normal">
                          {obs.notes}
                        </span>
                      )}
                    </td>

                    <td className="py-3 px-4">
                      <span className="font-bold text-slate-900 text-sm">
                        {obs.value_string}
                      </span>{' '}
                      <span className="text-slate-500 font-medium text-[11px]">
                        {obs.unit || ''}
                      </span>
                    </td>

                    <td className="py-3 px-4 text-slate-600 font-medium text-[11px]">
                      {obs.reference_range_text || 'Standard'}
                    </td>

                    <td className="py-3 px-4">
                      {getInterpretationBadge(obs.interpretation)}
                    </td>

                    <td className="py-3 px-4 text-right space-x-1">
                      <button
                        onClick={() => setEditingObs(obs)}
                        className="p-1.5 text-slate-500 hover:text-teal-700 hover:bg-teal-50 rounded-lg transition-colors cursor-pointer"
                        title={t('editTest')}
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>

                      {onDeleteObservation && (
                        <button
                          onClick={() => onDeleteObservation(obs.id)}
                          className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors cursor-pointer"
                          title="Delete test"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Edit Modal */}
      <LabResultEditModal
        observation={editingObs}
        isOpen={Boolean(editingObs)}
        onClose={() => setEditingObs(null)}
        onSave={onUpdateObservation}
      />
    </div>
  );
};
