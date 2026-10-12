import React, { useState } from 'react';
import {
  Sparkles,
  RefreshCw,
  Globe,
  HelpCircle,
  FileCheck,
  AlertTriangle,
  FileText
} from 'lucide-react';
import { KeyFinding } from '../types';
import { useLanguage } from '../context/LanguageContext';

interface AIExplanationCardProps {
  summaryEn?: string;
  summaryTa?: string;
  keyFindingsJson?: string;
  doctorQuestionsJson?: string;
  aiModel?: string;
  isDemoMode?: boolean;
  onRegenerate?: () => Promise<void>;
  onViewRawText?: () => void;
}

export const AIExplanationCard: React.FC<AIExplanationCardProps> = ({
  summaryEn = '',
  summaryTa = '',
  keyFindingsJson = '[]',
  doctorQuestionsJson = '[]',
  aiModel = 'MediMate Clinical Engine',
  isDemoMode = true,
  onRegenerate,
  onViewRawText,
}) => {
  const { language, setLanguage, t } = useLanguage();
  const [activeTab, setActiveTab] = useState<'en' | 'ta'>(language);
  const [isRegenerating, setIsRegenerating] = useState(false);

  let keyFindings: KeyFinding[] = [];
  try {
    keyFindings = JSON.parse(keyFindingsJson || '[]');
  } catch {
    keyFindings = [];
  }

  let doctorQuestions: string[] = [];
  try {
    doctorQuestions = JSON.parse(doctorQuestionsJson || '[]');
  } catch {
    doctorQuestions = [];
  }

  const handleRegenerate = async () => {
    if (!onRegenerate) return;
    setIsRegenerating(true);
    try {
      await onRegenerate();
    } finally {
      setIsRegenerating(false);
    }
  };

  // Switch display text based on active tab
  const displayText = activeTab === 'ta' && summaryTa ? summaryTa : summaryEn;

  // Helper to render inline markdown: **bold**, *italic* safely
  const renderInlineMarkdown = (text: string): React.ReactNode => {
    const parts: React.ReactNode[] = [];
    const regex = /(\*\*(.*?)\*\*|\*(.*?)\*)/g;
    let lastIndex = 0;
    let match: RegExpExecArray | null;

    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parts.push(text.slice(lastIndex, match.index));
      }
      if (match[2] !== undefined) {
        parts.push(
          <strong key={`b-${match.index}`} className="font-semibold text-slate-900">
            {match[2]}
          </strong>
        );
      } else if (match[3] !== undefined) {
        parts.push(
          <em key={`i-${match.index}`} className="italic text-slate-700">
            {match[3]}
          </em>
        );
      }
      lastIndex = regex.lastIndex;
    }

    if (lastIndex < text.length) {
      parts.push(text.slice(lastIndex));
    }

    return parts.length > 0 ? parts : text;
  };

  // Helper to render structured paragraphs, callout quotes, and bullet items
  const renderStructuredBlock = (block: string, blockIndex: number) => {
    const trimmed = block.trim();
    if (!trimmed) return null;

    // Callout quote / disclaimer
    if (trimmed.startsWith('>')) {
      const quoteContent = trimmed.replace(/^>\s*/, '');
      return (
        <div
          key={blockIndex}
          className="p-3 bg-amber-50/90 rounded-xl border-l-4 border-amber-500 text-amber-900 text-xs my-2 italic shadow-xs"
        >
          {renderInlineMarkdown(quoteContent)}
        </div>
      );
    }

    // Check if the block has line breaks with bullet lists
    const lines = trimmed.split('\n').map((l) => l.trim()).filter(Boolean);
    const hasBullets = lines.some((line) => /^[•\-\*]\s+/.test(line));

    if (hasBullets) {
      return (
        <div key={blockIndex} className="space-y-1.5 my-2">
          {lines.map((line, lineIdx) => {
            if (/^[•\-\*]\s+/.test(line)) {
              const cleanLine = line.replace(/^[•\-\*]\s+/, '');
              return (
                <div key={lineIdx} className="flex items-start gap-2 text-xs sm:text-sm pl-1">
                  <span className="text-teal-600 font-bold select-none mt-0.5">•</span>
                  <div className="flex-1 leading-relaxed text-slate-700">
                    {renderInlineMarkdown(cleanLine)}
                  </div>
                </div>
              );
            }
            return (
              <p key={lineIdx} className="leading-relaxed font-semibold text-slate-800 text-xs sm:text-sm mb-1">
                {renderInlineMarkdown(line)}
              </p>
            );
          })}
        </div>
      );
    }

    // Standard paragraph
    return (
      <p key={blockIndex} className="leading-relaxed text-slate-700 text-xs sm:text-sm">
        {renderInlineMarkdown(trimmed)}
      </p>
    );
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 overflow-hidden shadow-xs">
      {/* Header with Title, AI Model, Tab Switcher & Actions */}
      <div className="p-4 sm:p-5 bg-gradient-to-r from-teal-900 to-slate-900 text-white flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-teal-500/20 border border-teal-400/30 flex items-center justify-center text-teal-300">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-base text-white">
                {t('summaryTitle')}
              </h3>
              {isDemoMode ? (
                <span className="text-[10px] font-semibold bg-amber-400/20 text-amber-300 px-2 py-0.5 rounded-full border border-amber-400/30">
                  Demo AI Mode
                </span>
              ) : (
                <span className="text-[10px] font-semibold bg-teal-400/20 text-teal-300 px-2 py-0.5 rounded-full border border-teal-400/30">
                  Live LLM Active
                </span>
              )}
            </div>
            <p className="text-xs text-slate-300">
              Powered by {aiModel} • Plain language clinical synthesis
            </p>
          </div>
        </div>

        {/* Tab & Action buttons */}
        <div className="flex items-center gap-2">
          {/* Language Tabs */}
          <div className="bg-slate-800/80 p-0.5 rounded-xl border border-slate-700 flex items-center">
            <button
              onClick={() => setActiveTab('en')}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === 'en'
                  ? 'bg-teal-500 text-white shadow-xs'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              English
            </button>
            <button
              onClick={() => setActiveTab('ta')}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === 'ta'
                  ? 'bg-teal-500 text-white shadow-xs'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              தமிழ் (Tamil)
            </button>
          </div>

          {/* Regenerate summary button */}
          {onRegenerate && (
            <button
              onClick={handleRegenerate}
              disabled={isRegenerating}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs transition-colors cursor-pointer"
              title={t('regenerateSummary')}
            >
              <RefreshCw className={`w-4 h-4 ${isRegenerating ? 'animate-spin' : ''}`} />
            </button>
          )}

          {/* View Raw Text */}
          {onViewRawText && (
            <button
              onClick={onViewRawText}
              className="hidden sm:flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs transition-colors cursor-pointer"
              title={t('viewRawText')}
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Raw Text</span>
            </button>
          )}
        </div>
      </div>

      {/* Key Findings Highlights Cards */}
      {keyFindings.length > 0 && (
        <div className="p-4 bg-slate-50/70 border-b border-slate-100">
          <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2.5">
            {t('keyFindings')}
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5">
            {keyFindings.map((finding, idx) => {
              const isAttention = finding.status === 'Attention';
              return (
                <div
                  key={idx}
                  className={`p-3 rounded-xl border text-xs ${
                    isAttention
                      ? 'bg-amber-50/80 border-amber-200/90 text-amber-950'
                      : 'bg-white border-slate-200 text-slate-800'
                  }`}
                >
                  <div className="flex items-center gap-1.5 font-bold mb-1">
                    {isAttention ? (
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                    ) : (
                      <FileCheck className="w-3.5 h-3.5 text-teal-600 shrink-0" />
                    )}
                    <span>{finding.title}</span>
                  </div>
                  <p className="text-[11px] text-slate-600 leading-snug">
                    {finding.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Main Narrative Explanation */}
      <div className="p-5 space-y-4">
        <div className="prose prose-sm max-w-none text-slate-700 leading-relaxed space-y-3 text-xs sm:text-sm">
          {displayText ? (
            displayText
              .split('\n\n')
              .map((paragraph, index) => renderStructuredBlock(paragraph, index))
          ) : (
            <p className="italic text-slate-400">
              No AI summary available yet for this document.
            </p>
          )}
        </div>

        {/* Tailored Questions for Healthcare Professional */}
        {doctorQuestions.length > 0 && (
          <div className="mt-6 pt-4 border-t border-slate-100">
            <div className="flex items-center gap-2 mb-3">
              <div className="p-1 rounded-lg bg-teal-50 text-teal-700">
                <HelpCircle className="w-4 h-4" />
              </div>
              <h4 className="font-bold text-xs sm:text-sm text-slate-900">
                {t('questionsForDoctor')}
              </h4>
            </div>

            <div className="space-y-2">
              {doctorQuestions.map((question, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-2.5 p-3 rounded-xl bg-slate-50 border border-slate-100 text-xs text-slate-800"
                >
                  <span className="font-bold text-teal-600 shrink-0">{idx + 1}.</span>
                  <span className="leading-relaxed">{question}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
