export type InterpretationType = 'Normal' | 'High' | 'Low' | 'Critical' | 'Inconclusive';

export interface Observation {
  id: number;
  document_id: number;
  patient_id: number;
  code?: string;
  display_name: string;
  category?: string;
  value_string: string;
  value_quantity?: number | null;
  unit?: string | null;
  reference_range_low?: number | null;
  reference_range_high?: number | null;
  reference_range_text?: string | null;
  interpretation: InterpretationType;
  is_uncertain: boolean;
  user_corrected: boolean;
  confidence_score: number;
  notes?: string | null;
  effective_datetime?: string | null;
  created_at?: string;
}

export interface Condition {
  id: number;
  document_id: number;
  patient_id: number;
  code?: string;
  display_name: string;
  clinical_status: string;
  verification_status: string;
  category?: string;
  severity?: string;
  recorded_date?: string;
  notes?: string;
  created_at?: string;
}

export interface MedicationStatement {
  id: number;
  document_id: number;
  patient_id: number;
  medication_name: string;
  dosage_instruction?: string;
  route?: string;
  frequency?: string;
  status: string;
  effective_period?: string;
  notes?: string;
  created_at?: string;
}

export interface KeyFinding {
  title: string;
  description: string;
  status: 'Normal' | 'Attention' | 'Info';
}

export interface DocumentReference {
  id: number;
  patient_id: number;
  title: string;
  doc_type: string;
  category?: string;
  file_name: string;
  file_size: number;
  mime_type: string;
  report_date?: string;
  facility_name?: string;
  doctor_name?: string;
  status: string;
  raw_extracted_text?: string;
  summary_en?: string;
  summary_ta?: string;
  key_findings_json?: string;
  doctor_questions_json?: string;
  ai_model?: string;
  is_demo_mode: boolean;
  created_at?: string;
  observations: Observation[];
  conditions: Condition[];
  medications: MedicationStatement[];
}

export interface TimelineItem {
  id: number;
  title: string;
  doc_type: string;
  report_date: string;
  facility_name?: string;
  doctor_name?: string;
  file_name: string;
  total_observations: number;
  abnormal_observations: number;
  medications_count: number;
  conditions: string[];
  ai_model?: string;
  is_demo_mode: boolean;
  created_at?: string;
}

export interface DashboardStats {
  total_reports: number;
  total_tests: number;
  abnormal_tests_count: number;
  active_medications_count: number;
  recent_documents: DocumentReference[];
  recent_abnormal_observations: Observation[];
  health_timeline: Array<{
    id: number;
    title: string;
    doc_type: string;
    date: string;
    abnormal_count: number;
    facility: string;
  }>;
  is_demo_mode: boolean;
  active_ai_provider: string;
}

export interface SystemStatus {
  status: string;
  app_name: string;
  version: string;
  tesseract_installed: boolean;
  pdf_extraction: string;
  gemini_api_key_configured: boolean;
  active_ai_provider: string;
  is_demo_mode: boolean;
  database: string;
  max_upload_size_mb: number;
  supported_formats: string[];
}
