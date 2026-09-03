import { apiClient } from "@/lib/api-client";
import { AuthResponse, User } from "@/types";

export const authService = {
  async login(email: string, password: string): Promise<AuthResponse> {
    const data = await apiClient<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    if (typeof window !== "undefined") {
      localStorage.setItem("sih_token", data.access_token);
      localStorage.setItem("sih_user", JSON.stringify(data));
    }
    return data;
  },

  async getCurrentUser(): Promise<User> {
    return apiClient<User>("/auth/me");
  },

  logout() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("sih_token");
      localStorage.removeItem("sih_user");
      window.location.href = "/login";
    }
  },

  getStoredUser(): AuthResponse | null {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("sih_user");
      if (stored) {
        try {
          return JSON.parse(stored);
        } catch {
          return null;
        }
      }
    }
    return null;
  }
};
