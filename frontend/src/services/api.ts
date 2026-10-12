import {
  DocumentReference,
  Observation,
  DashboardStats,
  SystemStatus,
  TimelineItem
} from '../types';

const rawBase = import.meta.env.VITE_API_URL?.trim();
const API_BASE = rawBase
  ? `${rawBase.replace(/\/+$/, '').replace(/\/api$/, '')}/api`
  : '/api';

/**
 * Shared helper to resolve backend static-file URLs (e.g., /static/uploads or /static/samples).
 * Uses VITE_API_URL when set (stripping any /api suffix), while falling back to relative paths
 * to preserve localhost/dev-proxy behavior.
 */
export const getStaticUrl = (path: string): string => {
  if (!path) return '';
  if (/^https?:\/\//i.test(path)) return path;

  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  if (rawBase) {
    const backendOrigin = rawBase.replace(/\/+$/, '').replace(/\/api$/, '');
    return `${backendOrigin}${cleanPath}`;
  }
  return cleanPath;
};

export const api = {
  // Static Assets & URLs
  getStaticUrl,

  // Dashboard & Analytics
  async getDashboardStats(): Promise<DashboardStats> {
    const res = await fetch(`${API_BASE}/dashboard/stats`);
    if (!res.ok) throw new Error('Failed to load dashboard statistics');
    return res.json();
  },

  // Document Management
  async getDocuments(docType?: string): Promise<DocumentReference[]> {
    const url = docType && docType !== 'All' 
      ? `${API_BASE}/documents?doc_type=${encodeURIComponent(docType)}`
      : `${API_BASE}/documents`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch medical documents');
    return res.json();
  },

  async getDocumentById(id: number): Promise<DocumentReference> {
    const res = await fetch(`${API_BASE}/documents/${id}`);
    if (!res.ok) throw new Error(`Document #${id} not found`);
    return res.json();
  },

  async uploadDocument(formData: FormData): Promise<DocumentReference> {
    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Failed to upload document');
    }
    return res.json();
  },

  async loadSampleDocument(sampleKey: 'cbc' | 'lipid' = 'cbc'): Promise<DocumentReference> {
    const res = await fetch(`${API_BASE}/documents/load-sample?sample_key=${sampleKey}`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to load sample document');
    return res.json();
  },

  async deleteDocument(id: number): Promise<void> {
    const res = await fetch(`${API_BASE}/documents/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete document');
  },

  // Observation (Lab Result) Corrections
  async updateObservation(id: number, data: Partial<Observation>): Promise<Observation> {
    const res = await fetch(`${API_BASE}/observations/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update observation');
    return res.json();
  },

  async deleteObservation(id: number): Promise<void> {
    const res = await fetch(`${API_BASE}/observations/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete observation');
  },

  // AI Summary Actions
  async regenerateSummary(docId: number): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/documents/${docId}/regenerate-summary`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to regenerate AI summary');
    return res.json();
  },

  // Timeline
  async getTimeline(docType?: string, sortOrder: string = 'desc'): Promise<{ total_records: number; timeline: TimelineItem[] }> {
    const params = new URLSearchParams();
    if (docType && docType !== 'All') params.append('doc_type', docType);
    params.append('sort_order', sortOrder);
    
    const res = await fetch(`${API_BASE}/timeline?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch health timeline');
    return res.json();
  },

  // Settings & System
  async getSystemStatus(): Promise<SystemStatus> {
    const res = await fetch(`${API_BASE}/settings/status`);
    if (!res.ok) throw new Error('Failed to fetch system status');
    return res.json();
  },

  async seedData(): Promise<any> {
    const res = await fetch(`${API_BASE}/settings/seed-data`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to seed sample data');
    return res.json();
  },

  async resetDatabase(): Promise<any> {
    const res = await fetch(`${API_BASE}/settings/reset-database`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to reset database');
    return res.json();
  },

  async updateApiKey(geminiKey: string, forceDemo: boolean): Promise<any> {
    const res = await fetch(`${API_BASE}/settings/update-api-key`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        gemini_api_key: geminiKey,
        force_demo_mode: forceDemo,
      }),
    });
    if (!res.ok) throw new Error('Failed to update API settings');
    return res.json();
  },
};
