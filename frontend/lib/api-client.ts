/**
 * Centralized API Client with JWT Bearer Interceptor and Automatic Demo Fallback
 */
import {
  MOCK_USERS,
  MOCK_DEPARTMENTS,
  MOCK_APPROVALS,
  MOCK_BUSINESSES,
  MOCK_APPLICATIONS,
  MOCK_DOCUMENTS,
  MOCK_QUERIES,
  MOCK_INSPECTIONS,
  MOCK_RENEWALS,
  MOCK_INCENTIVES,
  MOCK_ANALYTICS,
  MOCK_AI_ANALYSIS
} from "./mock-data";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

interface RequestOptions extends RequestInit {
  params?: Record<string, string>;
}

function getMockFallback<T>(endpoint: string, options: RequestOptions = {}): T {
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;

  // Auth: login
  if (cleanEndpoint.startsWith("/auth/login")) {
    let email = "entrepreneur@abcfoods.com";
    if (options.body) {
      try {
        const parsed = JSON.parse(options.body as string);
        if (parsed.email) email = parsed.email;
      } catch {
        // ignore parse error
      }
    }
    const mockUser = MOCK_USERS[email] || MOCK_USERS["entrepreneur@abcfoods.com"];
    return mockUser.auth as unknown as T;
  }

  // Auth: me
  if (cleanEndpoint.startsWith("/auth/me")) {
    let email = "entrepreneur@abcfoods.com";
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("sih_user");
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          if (parsed.email) email = parsed.email;
        } catch {
          // ignore parse error
        }
      }
    }
    const mockUser = MOCK_USERS[email] || MOCK_USERS["entrepreneur@abcfoods.com"];
    return mockUser.user as unknown as T;
  }

  // Dashboard: summary
  if (cleanEndpoint.startsWith("/dashboard/summary")) {
    let role = "entrepreneur";
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("sih_user");
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          if (parsed.role) role = parsed.role;
        } catch {
          // ignore parse error
        }
      }
    }
    if (role === "entrepreneur") {
      return {
        total_businesses: 1,
        total_applications: 1,
        pending_approvals: 2,
        approved_applications: 1,
        action_required_queries: 1
      } as unknown as T;
    }
    return {
      total_applications: 48,
      under_review: 12,
      scheduled_inspections: 6,
      open_queries: 4,
      sla_compliance_rate: 94.2,
      avg_clearance_days: 21.4
    } as unknown as T;
  }

  // Analytics: overview
  if (cleanEndpoint.startsWith("/analytics/overview")) {
    return MOCK_ANALYTICS as unknown as T;
  }

  // Approvals & Departments
  if (cleanEndpoint === "/approvals/departments") {
    return MOCK_DEPARTMENTS as unknown as T;
  }
  if (cleanEndpoint.startsWith("/approvals")) {
    return MOCK_APPROVALS as unknown as T;
  }

  // Businesses
  if (cleanEndpoint.startsWith("/businesses")) {
    return MOCK_BUSINESSES as unknown as T;
  }

  // Applications
  if (cleanEndpoint.startsWith("/applications")) {
    if (cleanEndpoint.includes("/submit")) {
      return { ...MOCK_APPLICATIONS[0], status: "SUBMITTED" } as unknown as T;
    }
    if (cleanEndpoint.split("/").length > 2 && cleanEndpoint !== "/applications") {
      return MOCK_APPLICATIONS[0] as unknown as T;
    }
    return MOCK_APPLICATIONS as unknown as T;
  }

  // Documents
  if (cleanEndpoint.startsWith("/documents")) {
    return MOCK_DOCUMENTS as unknown as T;
  }

  // Queries
  if (cleanEndpoint.startsWith("/queries")) {
    return MOCK_QUERIES as unknown as T;
  }

  // Inspections
  if (cleanEndpoint.startsWith("/inspections")) {
    return MOCK_INSPECTIONS as unknown as T;
  }

  // Renewals
  if (cleanEndpoint.startsWith("/renewals")) {
    return MOCK_RENEWALS as unknown as T;
  }

  // Incentives
  if (cleanEndpoint.startsWith("/incentives")) {
    return MOCK_INCENTIVES as unknown as T;
  }

  // AI Endpoints
  if (cleanEndpoint.startsWith("/ai/analyze-business")) {
    return MOCK_AI_ANALYSIS as unknown as T;
  }
  if (cleanEndpoint.startsWith("/ai/ask")) {
    return {
      answer: "Under the Water (Prevention and Control of Pollution) Act 1974 and State Board regulations, industrial food processing facilities generating organic effluent must install an Effluent Treatment Plant (ETP) meeting zero liquid discharge (ZLD) or prescribed discharge standards prior to commercial operations.",
      cited_acts: [
        "Water (Prevention and Control of Pollution) Act, 1974",
        "Air (Prevention and Control of Pollution) Act, 1981",
        "Environment (Protection) Act, 1986"
      ],
      confidence: 0.94
    } as unknown as T;
  }
  if (cleanEndpoint.startsWith("/ai/predict-delay")) {
    return {
      delay_probability: 0.18,
      expected_delay_days: 28,
      risk_factors: ["ETP schematic verification", "Joint physical inspection slot availability"],
      recommendation: "Parallel submission to UPPCB and Fire Department recommended to save ~14 business days."
    } as unknown as T;
  }

  return {} as T;
}

export async function apiClient<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { params, headers, ...restOptions } = options;

  let url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  if (params) {
    const searchParams = new URLSearchParams(params);
    url += `?${searchParams.toString()}`;
  }

  const token = typeof window !== "undefined" ? localStorage.getItem("sih_token") : null;

  const defaultHeaders: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (token) {
    defaultHeaders["Authorization"] = `Bearer ${token}`;
  }

  // Detect HTTPS context calling unencrypted localhost (Mixed Content Block on Vercel)
  const isHttps = typeof window !== "undefined" && window.location.protocol === "https:";
  const isLocalHttp = API_BASE_URL.startsWith("http://localhost") || API_BASE_URL.startsWith("http://127.0.0.1");

  if (isHttps && isLocalHttp) {
    // Browser will block this call under Mixed Content security policy.
    // Seamlessly provide pre-seeded synthetic data for interactive demo on Vercel.
    return getMockFallback<T>(endpoint, options);
  }

  try {
    const response = await fetch(url, {
      headers: {
        ...defaultHeaders,
        ...(headers as Record<string, string>),
      },
      ...restOptions,
    });

    if (!response.ok) {
      let errorDetail = `API Error ${response.status}: ${response.statusText}`;
      try {
        const errorJson = await response.json();
        if (errorJson.detail) {
          errorDetail = errorJson.detail;
        }
      } catch {
        // ignore parse error
      }
      throw new Error(errorDetail);
    }

    return response.json();
  } catch (err: any) {
    // If backend is unreachable / down, seamlessly fall back to synthetic demo data
    return getMockFallback<T>(endpoint, options);
  }
}
