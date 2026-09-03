import { apiClient } from "@/lib/api-client";
import { AnalyzeBusinessResponse } from "@/types";

export interface AnalyzeBusinessParams {
  sector: string;
  location: string;
  investment: number;
  employees: number;
  business_details?: Record<string, any>;
}

export const aiService = {
  async analyzeBusiness(params: AnalyzeBusinessParams): Promise<AnalyzeBusinessResponse> {
    return apiClient<AnalyzeBusinessResponse>("/ai/analyze-business", {
      method: "POST",
      body: JSON.stringify(params),
    });
  },

  async askRegulatoryRAG(question: string, sector?: string, state?: string) {
    return apiClient<{ answer: string; cited_acts: string[]; confidence: number }>("/ai/ask", {
      method: "POST",
      body: JSON.stringify({ question, sector, state }),
    });
  },

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
  }
};
