import { apiClient } from "@/lib/api-client";
import {
  AnalyzeBusinessResponse,
  UnifiedComplianceAnalysisResponse,
  DocumentValidationResponse,
} from "@/types";

export interface AnalyzeBusinessParams {
  sector: string;
  location: string;
  investment: number;
  employees: number;
  business_details?: Record<string, any>;
}

export interface ComplianceAnalyzeParams {
  sector: string;
  state?: string;
  district?: string;
  investment: number;
  employees: number;
  project_stage?: string;
  connected_load_kw?: number;
  has_boiler?: boolean;
  is_food_business?: boolean;
  water_requirement_kld?: number;
  hazardous_materials?: boolean;
  built_up_area_sqm?: number;
  applicant_type?: string;
  business_id?: string;
  application_id?: string;
}

export interface DocumentValidateParams {
  document_id: string;
  filename: string;
  document_type: string;
  file_path?: string;
  file_content_text?: string;
  expected_entity_name?: string;
  expected_document_type?: string;
  application_id?: string;
}

export const aiService = {
  /**
   * Master multi-pillar compliance analysis calling Rule Engine, ML Predictor, and RAG.
   */
  async analyzeCompliance(params: ComplianceAnalyzeParams): Promise<UnifiedComplianceAnalysisResponse> {
    return apiClient<UnifiedComplianceAnalysisResponse>("/compliance/analyze", {
      method: "POST",
      body: JSON.stringify(params),
    });
  },

  /**
   * Backward-compatible business analyzer contract.
   */
  async analyzeBusiness(params: AnalyzeBusinessParams): Promise<AnalyzeBusinessResponse> {
    return apiClient<AnalyzeBusinessResponse>("/ai/analyze-business", {
      method: "POST",
      body: JSON.stringify(params),
    });
  },

  /**
   * Regulatory RAG statutory question answering.
   */
  async askRegulatoryRAG(question: string, sector?: string, state?: string) {
    return apiClient<{ answer: string; cited_acts: string[]; confidence: number; relevant_sections?: string[] }>("/ai/ask", {
      method: "POST",
      body: JSON.stringify({ question, sector, state }),
    });
  },

  /**
   * ML Delay and processing time predictor.
   */
  async predictDelay(params: {
    sector: string;
    state: string;
    investment: number;
    approval_codes: string[];
    document_count: number;
    has_hazardous?: boolean;
  }) {
    return apiClient<{ delay_probability: number; expected_delay_days: number; risk_factors: string[]; recommendation: string }>("/ai/predict-delay", {
      method: "POST",
      body: JSON.stringify(params),
    });
  },

  /**
   * Document AI pre-validation for uploaded documents.
   */
  async validateDocument(params: DocumentValidateParams): Promise<DocumentValidationResponse> {
    return apiClient<DocumentValidationResponse>("/documents/validate", {
      method: "POST",
      body: JSON.stringify(params),
    });
  },

  /**
   * Health probe for all 4 AI/ML modules.
   */
  async checkComplianceHealth() {
    return apiClient<{ status: string; rule_engine: any; ml_predictor: any; rag_pipeline: any; document_ai: any }>("/compliance/health", {
      method: "GET",
    });
  }
};

