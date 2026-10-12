import React, { useState, useEffect } from 'react';
import {
  Settings as SettingsIcon,
  Globe,
  Key,
  Database,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Cpu,
  Shield,
  User,
  Sparkles
} from 'lucide-react';
import { SystemStatus } from '../types';
import { api } from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import { MedicalDisclaimer } from '../components/MedicalDisclaimer';

export const SettingsPage: React.FC = () => {
  const { language, setLanguage, t } = useLanguage();

  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [forceDemo, setForceDemo] = useState(false);
  const [savingKey, setSavingKey] = useState(false);
  const [keySuccess, setKeySuccess] = useState<string | null>(null);
  const [resettingData, setResettingData] = useState(false);
  const [resetSuccess, setResetSuccess] = useState<string | null>(null);

  const loadStatus = async () => {
    try {
      const data = await api.getSystemStatus();
      setSystemStatus(data);
      setForceDemo(data.is_demo_mode);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleSaveApiKey = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingKey(true);
    setKeySuccess(null);
    try {
      const res = await api.updateApiKey(apiKeyInput, forceDemo);
      setKeySuccess('API settings updated successfully.');
      setApiKeyInput('');
      loadStatus();
    } catch (err: any) {
      alert(err.message || 'Failed to update key');
    } finally {
      setSavingKey(false);
    }
  };

  const handleResetData = async () => {
    if (!confirm('Resetting will clear all existing reports and re-seed the standard synthetic demo patient records. Continue?')) {
      return;
    }
    setResettingData(true);
    setResetSuccess(null);
    try {
      await api.resetDatabase();
      setResetSuccess(t('dataSeededSuccess'));
      loadStatus();
    } catch (err: any) {
      alert(err.message || 'Failed to reset database');
    } finally {
      setResettingData(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">
          {t('settingsTitle')}
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Configure language preferences, AI engine credentials, and synthetic demonstration datasets.
        </p>
      </div>

      <MedicalDisclaimer compact={true} />

      {/* 1. Language Preference Section */}
      <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs space-y-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-teal-50 text-teal-700 rounded-xl">
            <Globe className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-bold text-sm text-slate-900">
              {t('languageSetting')}
            </h2>
            <p className="text-xs text-slate-500">
              Select primary language for navigation, alerts, and medical explanations.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
          <button
            onClick={() => setLanguage('en')}
            className={`p-4 rounded-xl border text-left transition-all cursor-pointer ${
              language === 'en'
                ? 'border-teal-500 bg-teal-50/50 shadow-xs ring-2 ring-teal-500/20'
                : 'border-slate-200 bg-slate-50/50 hover:bg-slate-100'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="font-bold text-sm text-slate-900">English</span>
              {language === 'en' && <CheckCircle2 className="w-4 h-4 text-teal-600" />}
            </div>
            <p className="text-xs text-slate-500">
              Standard clinical terms, reference ranges, and doctor questions in English.
            </p>
          </button>

          <button
            onClick={() => setLanguage('ta')}
            className={`p-4 rounded-xl border text-left transition-all cursor-pointer ${
              language === 'ta'
                ? 'border-teal-500 bg-teal-50/50 shadow-xs ring-2 ring-teal-500/20'
                : 'border-slate-200 bg-slate-50/50 hover:bg-slate-100'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="font-bold text-sm text-slate-900">தமிழ் (Tamil)</span>
              {language === 'ta' && <CheckCircle2 className="w-4 h-4 text-teal-600" />}
            </div>
            <p className="text-xs text-slate-500">
              பரிசோதனை பெயர்கள் மற்றும் அளவுகள் மாறாமல் எளிய தமிழில் விளக்கங்கள்.
            </p>
          </button>
        </div>
      </div>

      {/* 2. AI Model & API Configuration */}
      <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-teal-50 text-teal-700 rounded-xl">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-bold text-sm text-slate-900">
                {t('apiKeySetting')}
              </h2>
              <p className="text-xs text-slate-500">
                Current Engine: <strong className="text-teal-700">{systemStatus?.active_ai_provider || 'MediMate Clinical Engine'}</strong>
              </p>
            </div>
          </div>

          <span
            className={`text-[11px] font-bold px-2.5 py-1 rounded-full border ${
              systemStatus?.gemini_api_key_configured
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                : 'bg-amber-50 text-amber-800 border-amber-200'
            }`}
          >
            {systemStatus?.gemini_api_key_configured ? 'API Key Configured' : 'Demo Mode Active'}
          </span>
        </div>

        <form onSubmit={handleSaveApiKey} className="space-y-3 pt-2">
          {keySuccess && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              <span>{keySuccess}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Google Gemini API Key
            </label>
            <div className="relative">
              <input
                type="password"
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
                placeholder="Enter AIzaSy... (Leave empty to use built-in Clinical Heuristic Demo Mode)"
                className="w-full px-3.5 py-2.5 text-xs rounded-xl border border-slate-300 font-mono focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
              />
            </div>
            <p className="text-[11px] text-slate-400 mt-1">
              MediMate AI never exposes API keys in frontend code. Keys are stored safely in backend memory for evaluation.
            </p>
          </div>

          <div className="flex items-center justify-between pt-1">
            <label className="flex items-center gap-2 text-xs text-slate-700 font-medium cursor-pointer">
              <input
                type="checkbox"
                checked={forceDemo}
                onChange={(e) => setForceDemo(e.target.checked)}
                className="rounded text-teal-600 focus:ring-teal-500"
              />
              <span>Force Demo Mode (Use rule-based clinical engine even if key is set)</span>
            </label>

            <button
              type="submit"
              disabled={savingKey}
              className="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-bold transition-colors cursor-pointer"
            >
              {savingKey ? 'Saving...' : 'Update Settings'}
            </button>
          </div>
        </form>
      </div>

      {/* 3. Demo Dataset Management */}
      <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs space-y-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-slate-100 text-slate-700 rounded-xl">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-bold text-sm text-slate-900">
              Demo Database Management
            </h2>
            <p className="text-xs text-slate-500">
              Re-seed standard synthetic patient profiles and clinical lab reports.
            </p>
          </div>
        </div>

        {resetSuccess && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            <span>{resetSuccess}</span>
          </div>
        )}

        <div className="flex items-center justify-between pt-1">
          <p className="text-xs text-slate-600 max-w-md">
            Wipes any uploaded user files and re-creates synthetic patient <strong>Arun Kumar</strong> with sample CBC and Lipid panel reports.
          </p>

          <button
            onClick={handleResetData}
            disabled={resettingData}
            className="flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-xl text-xs font-bold transition-colors cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${resettingData ? 'animate-spin' : ''}`} />
            <span>{resettingData ? 'Resetting...' : t('resetData')}</span>
          </button>
        </div>
      </div>

      {/* 4. System Diagnostics */}
      <div className="bg-slate-50 rounded-2xl border border-slate-200 p-5 text-xs space-y-3">
        <h3 className="font-bold text-slate-900 flex items-center gap-2">
          <Cpu className="w-4 h-4 text-teal-600" />
          System &amp; Architectural Diagnostics
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-slate-600">
          <div>
            <span className="text-[10px] uppercase font-bold text-slate-400 block">Database</span>
            <strong className="text-slate-900">{systemStatus?.database || 'SQLite'}</strong>
          </div>
          <div>
            <span className="text-[10px] uppercase font-bold text-slate-400 block">PDF Engine</span>
            <strong className="text-slate-900">{systemStatus?.pdf_extraction || 'Active'}</strong>
          </div>
          <div>
            <span className="text-[10px] uppercase font-bold text-slate-400 block">OCR Engine</span>
            <strong className="text-slate-900">
              {systemStatus?.tesseract_installed ? 'Tesseract Native' : 'Digital PDF / Heuristic OCR'}
            </strong>
          </div>
          <div>
            <span className="text-[10px] uppercase font-bold text-slate-400 block">Max Upload</span>
            <strong className="text-slate-900">{systemStatus?.max_upload_size_mb || 15} MB</strong>
          </div>
        </div>
      </div>
    </div>
  );
};
