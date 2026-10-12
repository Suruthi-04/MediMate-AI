import React from 'react';
import {
  Activity,
  ArrowRight,
  ShieldCheck,
  FileSearch,
  Languages,
  Clock,
  Sparkles,
  UploadCloud,
  CheckCircle2,
  AlertTriangle,
  Stethoscope
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { MedicalDisclaimer } from '../components/MedicalDisclaimer';

interface LandingPageProps {
  onGetStarted: () => void;
  onExploreDemo: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onGetStarted,
  onExploreDemo,
}) => {
  const { t, language } = useLanguage();

  const features = [
    {
      icon: UploadCloud,
      title: "Document Ingestion & OCR",
      desc: "Extract text seamlessly from digital diagnostic PDFs, mobile photos, and scanned clinical documents.",
      tag: "PDF / PNG / JPG"
    },
    {
      icon: FileSearch,
      title: "Medical Document Intelligence",
      desc: "Automatically extracts test names, numeric values, units, biological reference intervals, and flagged out-of-range results.",
      tag: "Lab Tests & Meds"
    },
    {
      icon: Sparkles,
      title: "AI Health Summary & Questions",
      desc: "Generates clear, simple explanations with tailored questions to discuss with your healthcare professional.",
      tag: "LLM + Safety Guardrails"
    },
    {
      icon: Languages,
      title: "Tamil Language Localization",
      desc: "Translates findings into polite, natural Tamil while preserving exact medical test names and measurement units.",
      tag: "English & தமிழ்"
    },
    {
      icon: Clock,
      title: "Unified Health Timeline",
      desc: "A centralized, chronological record of your health history built on a FHIR-inspired SQLite architecture.",
      tag: "FHIR-Inspired"
    },
    {
      icon: ShieldCheck,
      title: "Human-in-the-Loop Verification",
      desc: "Mark uncertain OCR lines for easy manual review. Never invents missing data and preserves raw text for audit.",
      tag: "Audit Trail"
    }
  ];

  return (
    <div className="space-y-12 py-4">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-b from-teal-900 via-slate-900 to-slate-950 text-white p-8 sm:p-12 lg:p-16 shadow-xl border border-slate-800">
        <div className="relative z-10 max-w-3xl space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-teal-500/20 border border-teal-400/30 text-teal-300 text-xs font-semibold uppercase tracking-wider">
            <Activity className="w-4 h-4 text-teal-400 animate-pulse" />
            <span>HacXLerate 2026 • Round 1 • Challenge 1</span>
          </div>

          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight">
            MediMate AI <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-emerald-300">
              Personal Health Copilot
            </span>
          </h1>

          <p className="text-slate-300 text-sm sm:text-base lg:text-lg leading-relaxed max-w-2xl">
            Empowering patients to upload complex medical records, parse laboratory values against clinical reference bounds, understand findings in plain language (English &amp; தமிழ்), and track a unified health timeline.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <button
              onClick={onGetStarted}
              className="flex items-center gap-2 px-6 py-3.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-sm shadow-lg shadow-teal-500/25 transition-all transform hover:-translate-y-0.5 cursor-pointer"
            >
              <span>{t('getStarted')}</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={onExploreDemo}
              className="flex items-center gap-2 px-6 py-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 font-semibold text-sm transition-all cursor-pointer"
            >
              <Stethoscope className="w-4 h-4 text-teal-400" />
              <span>Explore Demo Dashboard</span>
            </button>
          </div>

          <div className="pt-4 flex flex-wrap items-center gap-6 text-xs text-slate-400">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-teal-400" /> Zero Hallucination Guard
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-teal-400" /> No Diagnosis / Non-Prescriptive
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-teal-400" /> English &amp; Tamil AI Support
            </span>
          </div>
        </div>

        {/* Decorative background glow */}
        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl pointer-events-none" />
      </section>

      {/* Persistent Medical Disclaimer */}
      <MedicalDisclaimer />

      {/* Core Features Grid */}
      <section className="space-y-6">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Comprehensive Clinical Intelligence
          </h2>
          <p className="text-xs sm:text-sm text-slate-500">
            Engineered specifically for patient health literacy, transparency, and clinical auditability.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((feat, idx) => {
            const Icon = feat.icon;
            return (
              <div
                key={idx}
                className="bg-white rounded-2xl p-6 border border-slate-200/90 shadow-xs hover:shadow-md transition-all hover:border-teal-300 group"
              >
                <div className="flex items-center justify-between gap-2 mb-4">
                  <div className="w-10 h-10 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center group-hover:bg-teal-600 group-hover:text-white transition-colors">
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-bold bg-slate-100 text-slate-600 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
                    {feat.tag}
                  </span>
                </div>
                <h3 className="font-bold text-slate-900 text-base mb-2">
                  {feat.title}
                </h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  {feat.desc}
                </p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Workflow Section */}
      <section className="bg-slate-50 border border-slate-200 rounded-3xl p-8 sm:p-10 space-y-6">
        <h3 className="font-bold text-xl text-slate-900 text-center">
          How MediMate AI Works
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-center">
          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-xs">
            <span className="w-7 h-7 rounded-full bg-teal-600 text-white font-bold text-xs inline-flex items-center justify-center mb-2">1</span>
            <h4 className="font-bold text-sm text-slate-900">Upload Record</h4>
            <p className="text-[11px] text-slate-500 mt-1">Upload digital PDF or photo of lab test, prescription, or discharge summary.</p>
          </div>

          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-xs">
            <span className="w-7 h-7 rounded-full bg-teal-600 text-white font-bold text-xs inline-flex items-center justify-center mb-2">2</span>
            <h4 className="font-bold text-sm text-slate-900">OCR &amp; Extraction</h4>
            <p className="text-[11px] text-slate-500 mt-1">Extracts investigations, numerical values, units, and laboratory reference ranges.</p>
          </div>

          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-xs">
            <span className="w-7 h-7 rounded-full bg-teal-600 text-white font-bold text-xs inline-flex items-center justify-center mb-2">3</span>
            <h4 className="font-bold text-sm text-slate-900">AI Health Summary</h4>
            <p className="text-[11px] text-slate-500 mt-1">Synthesizes easy-to-read insights in English and Tamil with tailored doctor questions.</p>
          </div>

          <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-xs">
            <span className="w-7 h-7 rounded-full bg-teal-600 text-white font-bold text-xs inline-flex items-center justify-center mb-2">4</span>
            <h4 className="font-bold text-sm text-slate-900">Health Timeline</h4>
            <p className="text-[11px] text-slate-500 mt-1">Persists to FHIR-inspired SQLite timeline for long-term health tracking and review.</p>
          </div>
        </div>
      </section>
    </div>
  );
};
