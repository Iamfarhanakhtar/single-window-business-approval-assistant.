import { apiClient } from "@/lib/api-client";
import { Approval, Department, Incentive, Renewal, Business } from "@/types";

export const approvalService = {
  async getApprovals(): Promise<Approval[]> {
    return apiClient<Approval[]>("/approvals");
  },

  async getDepartments(): Promise<Department[]> {
    return apiClient<Department[]>("/approvals/departments");
  },

  async getBusinesses(): Promise<Business[]> {
    return apiClient<Business[]>("/businesses");
  },

  async getIncentives(): Promise<Incentive[]> {
    return apiClient<Incentive[]>("/incentives");
  },

  async getRenewals(): Promise<Renewal[]> {
    return apiClient<Renewal[]>("/renewals");
  }
};
