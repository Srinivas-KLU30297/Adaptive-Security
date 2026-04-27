export interface ModalityResultOut {
  id: string;
  modality: string;
  verdict: string;
  confidence: number;
  xai_data: any;
  processing_time_ms: number;
  created_at: string;
}

export interface CaseOut {
  id: string;
  user_id: string;
  case_type: string;
  input_summary?: string;
  verdict?: string;
  confidence?: number;
  risk_level?: string;
  status: string;
  report_path?: string;
  created_at: string;
  updated_at: string;
  modality_results: ModalityResultOut[];
}

export interface CaseListResponse {
  items: CaseOut[];
  total: number;
  page: number;
  size: number;
}
