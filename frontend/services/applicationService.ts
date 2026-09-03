import { apiClient } from "@/lib/api-client";
import { Application, DocumentItem, QueryRecord, Inspection } from "@/types";

export const applicationService = {
  async getApplications(statusFilter?: string): Promise<Application[]> {
    const params: Record<string, string> = {};
    if (statusFilter) params["status_filter"] = statusFilter;
    return apiClient<Application[]>("/applications", { params });
  },

  async getApplicationById(id: string): Promise<Application> {
    return apiClient<Application>(`/applications/${id}`);
  },

  async createApplication(businessId: string, approvalIds: string[]): Promise<Application> {
    return apiClient<Application>("/applications", {
      method: "POST",
      body: JSON.stringify({ business_id: businessId, approval_ids: approvalIds }),
    });
  },

  async submitApplication(id: string): Promise<Application> {
    return apiClient<Application>(`/applications/${id}/submit`, {
      method: "POST",
    });
  },

  async getDocuments(applicationId?: string, businessId?: string): Promise<DocumentItem[]> {
    const params: Record<string, string> = {};
    if (applicationId) params["application_id"] = applicationId;
    if (businessId) params["business_id"] = businessId;
    return apiClient<DocumentItem[]>("/documents", { params });
  },

  async getQueries(applicationId?: string): Promise<QueryRecord[]> {
    const params: Record<string, string> = {};
    if (applicationId) params["application_id"] = applicationId;
    return apiClient<QueryRecord[]>("/queries", { params });
  },

  async getInspections(applicationId?: string): Promise<Inspection[]> {
    const params: Record<string, string> = {};
    if (applicationId) params["application_id"] = applicationId;
    return apiClient<Inspection[]>("/inspections", { params });
  }
};
