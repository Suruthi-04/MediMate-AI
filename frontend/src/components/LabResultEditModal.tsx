import React, { useState, useEffect } from 'react';
import { X, Check, AlertCircle } from 'lucide-react';
import { Observation } from '../types';
import { useLanguage } from '../context/LanguageContext';

interface LabResultEditModalProps {
  observation: Observation | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (obsId: number, updated: Partial<Observation>) => Promise<void>;
}

export const LabResultEditModal: React.FC<LabResultEditModalProps> = ({
  observation,
  isOpen,
  onClose,
  onSave,
}) => {
  const { t } = useLanguage();
  const [displayName, setDisplayName] = useState('');
  const [valueString, setValueString] = useState('');
  const [unit, setUnit] = useState('');
  const [refText, setRefText] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (observation) {
      setDisplayName(observation.display_name || '');
      setValueString(observation.value_string || '');
      setUnit(observation.unit || '');
      setRefText(observation.reference_range_text || '');
      setNotes(observation.notes || '');
      setError(null);
    }
  }, [observation]);

  if (!isOpen || !observation) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!valueString.trim()) {
      setError('Value is required');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await onSave(observation.id, {
        display_name: displayName,
        value_string: valueString,
        unit: unit,
        reference_range_text: refText,
        notes: notes,
      });
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to update observation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs">
      <div className="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-900 text-base">
              {t('editTest')}
            </h3>
            <p className="text-xs text-slate-500">
              Manual correction of OCR-extracted parameter
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/50 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              {t('testName')}
            </label>
            <input
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                {t('observedValue')}
              </label>
              <input
                type="text"
                value={valueString}
                onChange={(e) => setValueString(e.target.value)}
                placeholder="e.g. 11.2"
                className="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                {t('unit')}
              </label>
              <input
                type="text"
                value={unit}
                onChange={(e) => setUnit(e.target.value)}
                placeholder="e.g. g/dL, mg/dL"
                className="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              {t('referenceRange')}
            </label>
            <input
              type="text"
              value={refText}
              onChange={(e) => setRefText(e.target.value)}
              placeholder="e.g. 13.0 - 17.0 g/dL"
              className="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Verification Notes (Optional)
            </label>
            <textarea
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g. Corrected against original printed laboratory receipt"
              className="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
            />
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 text-xs font-medium text-slate-600 hover:text-slate-900 rounded-xl hover:bg-slate-100 transition-colors"
            >
              {t('cancel')}
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-teal-600 hover:bg-teal-700 rounded-xl shadow-xs transition-colors cursor-pointer"
            >
              <Check className="w-3.5 h-3.5" />
              <span>{loading ? 'Saving...' : t('saveChanges')}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
