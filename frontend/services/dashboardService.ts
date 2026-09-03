import { apiClient } from "@/lib/api-client";

export const dashboardService = {
  async getSummary(): Promise<any> {
    return apiClient<any>("/dashboard/summary");
  },

  async getAnalytics(): Promise<any> {
    return apiClient<any>("/analytics/overview");
  }
};
