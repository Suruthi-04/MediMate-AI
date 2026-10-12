import React, { useState, useRef } from 'react';
import {
  UploadCloud,
  FileText,
  Image as ImageIcon,
  CheckCircle,
  AlertCircle,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  RefreshCw,
  FileCheck
} from 'lucide-react';
import { api } from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import { MedicalDisclaimer } from '../components/MedicalDisclaimer';

interface UploadPageProps {
  onUploadSuccess: (newDocId: number) => void;
}

export const UploadPage: React.FC<UploadPageProps> = ({ onUploadSuccess }) => {
  const { t } = useLanguage();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [docTitle, setDocTitle] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [loadingSample, setLoadingSample] = useState<string | null>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  };

  const handleFileSelected = (file: File) => {
    setError(null);
    const validExtensions = ['.pdf', '.png', '.jpg', '.jpeg'];
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();

    if (!validExtensions.includes(ext)) {
      setError(`Invalid file format '${ext}'. Allowed: PDF, PNG, JPG, JPEG.`);
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      setError('File exceeds 15MB limit. Please upload a smaller document.');
      return;
    }

    setSelectedFile(file);
    if (!docTitle) {
      // Suggest clean title from file name
      const cleanName = file.name.replace(/\.[^/.]+$/, '').replace(/[_\\-]/g, ' ');
      setDocTitle(cleanName);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Please select a medical document to upload');
      return;
    }

    setIsUploading(true);
    setUploadProgress(20);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    if (docTitle.trim()) {
      formData.append('doc_title', docTitle.trim());
    }

    try {
      // Simulate stepped progress for OCR analysis
      const timer = setInterval(() => {
        setUploadProgress((prev) => (prev < 85 ? prev + 15 : prev));
      }, 300);

      const response = await api.uploadDocument(formData);
      clearInterval(timer);
      setUploadProgress(100);

      setTimeout(() => {
        onUploadSuccess(response.id);
      }, 500);
    } catch (err: any) {
      setError(err.message || 'Upload and analysis failed. Please try again.');
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleLoadSample = async (sampleType: 'cbc' | 'lipid') => {
    setLoadingSample(sampleType);
    setError(null);
    try {
      const doc = await api.loadSampleDocument(sampleType);
      onUploadSuccess(doc.id);
    } catch (err: any) {
      setError(err.message || 'Failed to load sample');
    } finally {
      setLoadingSample(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">
          {t('uploadDocument')}
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Upload laboratory test results, hospital discharge summaries, or prescriptions for OCR extraction and AI plain-language synthesis.
        </p>
      </div>

      <MedicalDisclaimer compact={true} />

      {/* 1-Click Demonstration Shortcuts */}
      <div className="bg-gradient-to-r from-teal-50 to-slate-50 border border-teal-200/80 rounded-2xl p-4 sm:p-5">
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="w-4 h-4 text-teal-600" />
          <h3 className="font-bold text-xs sm:text-sm text-slate-900">
            Hackathon Live Evaluation: 1-Click Sample Reports
          </h3>
        </div>
        <p className="text-xs text-slate-600 mb-3 leading-relaxed">
          Don't have a medical report on hand? Test the complete extraction, reference range flagging, and dual-language AI summaries instantly with realistic synthetic records:
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => handleLoadSample('cbc')}
            disabled={Boolean(loadingSample) || isUploading}
            className="flex items-center justify-between p-3.5 bg-white border border-teal-200 hover:border-teal-400 rounded-xl text-left transition-all hover:shadow-xs group cursor-pointer"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-teal-50 text-teal-700">
                <FileText className="w-4 h-4" />
              </div>
              <div>
                <span className="font-bold text-xs text-slate-900 block group-hover:text-teal-700">
                  Complete Blood Count (CBC)
                </span>
                <span className="text-[11px] text-slate-500">
                  Synthetic PDF • Hemoglobin, WBC, Platelets
                </span>
              </div>
            </div>
            {loadingSample === 'cbc' ? (
              <RefreshCw className="w-4 h-4 text-teal-600 animate-spin" />
            ) : (
              <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-teal-600 transition-transform group-hover:translate-x-1" />
            )}
          </button>

          <button
            type="button"
            onClick={() => handleLoadSample('lipid')}
            disabled={Boolean(loadingSample) || isUploading}
            className="flex items-center justify-between p-3.5 bg-white border border-teal-200 hover:border-teal-400 rounded-xl text-left transition-all hover:shadow-xs group cursor-pointer"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-teal-50 text-teal-700">
                <FileText className="w-4 h-4" />
              </div>
              <div>
                <span className="font-bold text-xs text-slate-900 block group-hover:text-teal-700">
                  Diabetic &amp; Lipid Profile
                </span>
                <span className="text-[11px] text-slate-500">
                  Synthetic PDF • HbA1c, FBS, Cholesterol
                </span>
              </div>
            </div>
            {loadingSample === 'lipid' ? (
              <RefreshCw className="w-4 h-4 text-teal-600 animate-spin" />
            ) : (
              <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-teal-600 transition-transform group-hover:translate-x-1" />
            )}
          </button>
        </div>
      </div>

      {/* Main Upload Drag & Drop Form */}
      <form onSubmit={handleUploadSubmit} className="bg-white rounded-2xl border border-slate-200/90 p-6 space-y-5 shadow-xs">
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-xs flex items-center gap-2.5">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Drag & Drop Box */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer ${
            isDragging
              ? 'border-teal-500 bg-teal-50/50'
              : 'border-slate-300 hover:border-teal-400 bg-slate-50/50 hover:bg-white'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg"
            onChange={handleFileChange}
            className="hidden"
          />

          <div className="w-14 h-14 rounded-2xl bg-teal-100 text-teal-700 mx-auto flex items-center justify-center mb-3">
            <UploadCloud className="w-7 h-7" />
          </div>

          <h3 className="font-bold text-slate-900 text-sm mb-1">
            {selectedFile ? selectedFile.name : 'Click to select or drag and drop medical document'}
          </h3>

          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Supports electronic and scanned PDFs, PNG, and JPG images up to 15MB.
          </p>

          {selectedFile && (
            <div className="mt-4 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-800 text-xs font-semibold border border-emerald-200">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
              <span>
                Selected: {(selectedFile.size / 1024).toFixed(1)} KB
              </span>
            </div>
          )}
        </div>

        {/* Document Title Input */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1.5">
            Document Title (Optional)
          </label>
          <input
            type="text"
            value={docTitle}
            onChange={(e) => setDocTitle(e.target.value)}
            placeholder="e.g. Annual Blood Examination 2026"
            className="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
          />
        </div>

        {/* Upload Progress Bar */}
        {isUploading && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
              <span className="flex items-center gap-1.5">
                <RefreshCw className="w-3.5 h-3.5 text-teal-600 animate-spin" />
                Extracting text, running OCR &amp; structuring clinical observations...
              </span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-teal-600 transition-all duration-300 ease-out"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="flex items-center justify-between pt-2">
          <div className="flex items-center gap-1.5 text-slate-500 text-xs">
            <ShieldCheck className="w-4 h-4 text-teal-600" />
            <span>Secure local extraction</span>
          </div>

          <button
            type="submit"
            disabled={!selectedFile || isUploading}
            className="flex items-center gap-2 px-6 py-2.5 bg-teal-600 hover:bg-teal-700 disabled:bg-slate-300 text-white font-bold text-xs sm:text-sm rounded-xl shadow-xs transition-colors cursor-pointer"
          >
            <span>{isUploading ? 'Analyzing...' : 'Analyze Document'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
};
