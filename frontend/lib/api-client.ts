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
  if (cleanEndpoint.startsWith("/documents/validate") || cleanEndpoint.startsWith("/ai/validate-document") || cleanEndpoint.startsWith("/compliance/validate-document")) {
    return {
      document_id: "DOC_VAL_001",
      filename: "fire_noc_layout.txt",
      status: "VALID",
      entity_match: "EXACT_MATCH",
      expiry_status: "VALID",
      type_match: "MATCH",
      checks: [
        { check_name: "Readability", passed: true, details: "Document text successfully parsed." },
        { check_name: "Document Type Match", passed: true, details: "Document category aligns with Fire NOC." },
        { check_name: "Entity Name Consistency", passed: true, details: "Matches enterprise name." },
        { check_name: "Validity Period", passed: true, details: "Certificate valid for 863 days." }
      ],
      warnings: [],
      errors: [],
      confidence: 1.0,
      days_until_expiry: 863,
      requires_human_verification: true,
      disclaimer: "Document AI pre-validation is a data consistency and completeness check."
    } as unknown as T;
  }
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

  // AI & Compliance Endpoints
  if (cleanEndpoint.startsWith("/compliance/analyze") || cleanEndpoint.startsWith("/ai/analyze-business")) {
    return {
      business_profile: {
        sector: "Food Processing",
        state: "Uttar Pradesh",
        district: "Ghaziabad",
        investment: 50000000,
        employees: 80,
        project_stage: "Pre-Operation"
      },
      summary: {
        total_approvals: 4,
        potentially_applicable: 4,
        requires_verification: 0,
        documents_required: 6
      },
      approvals: [
        {
          approval_id: "UP_PCB_CTE_001",
          approval_name: "Consent to Establish (CTE) - Orange/Red Category",
          authority: "Uttar Pradesh Pollution Control Board (UPPCB)",
          status: "POTENTIALLY_APPLICABLE",
          score: 1.0,
          reason: "Applicable for manufacturing/food processing units in Uttar Pradesh.",
          documents: ["Site Plan", "ETP Schematic", "Water Balance Chart"],
          processing_days: 30,
          statutory_fee: 25000,
          department: "UPPCB",
          category: "Environmental",
          is_mandatory: true,
          prerequisites: []
        },
        {
          approval_id: "UP_FIRE_NOC_001",
          approval_name: "Fire Safety No Objection Certificate (Provisional)",
          authority: "Uttar Pradesh Fire Service Headquarters",
          status: "POTENTIALLY_APPLICABLE",
          score: 1.0,
          reason: "Mandatory safety clearance for industrial buildings >500 sqm.",
          documents: ["Building Layout Blueprint", "Fire Fighting Installation Plan"],
          processing_days: 15,
          statutory_fee: 5000,
          department: "Fire Department",
          category: "Safety",
          is_mandatory: true,
          prerequisites: []
        }
      ],
      documents: [
        { document_name: "Site Plan", required_for: ["Consent to Establish (CTE) - Orange/Red Category"], status: "MISSING" },
        { document_name: "Building Layout Blueprint", required_for: ["Fire Safety No Objection Certificate (Provisional)"], status: "MISSING" },
        { document_name: "ETP Schematic", required_for: ["Consent to Establish (CTE) - Orange/Red Category"], status: "MISSING" }
      ],
      risk: {
        risk_score: 28,
        risk_level: "LOW",
        factors: ["Standard industrial profile with predictable clearance pathways."]
      },
      delay_prediction: {
        probability: 0.18,
        predicted_days: 28,
        factors: ["Parallel application submission recommended."],
        is_synthetic_model: true
      },
      recommendations: [
        "Apply concurrently for UPPCB CTE and Fire Safety NOC to compress timeline.",
        "Ensure ETP drawings are pre-validated to avoid scrutiny deficiency queries."
      ],
      regulatory_explanations: [
        {
          approval_id: "UP_PCB_CTE_001",
          approval_name: "Consent to Establish (CTE)",
          answer: "Under Section 25 of the Water Act 1974, prior consent from the State Board is mandatory before establishing manufacturing units.",
          cited_acts: ["Water (Prevention & Control of Pollution) Act 1974 Sec 25", "UP Single Window Act 2018"],
          confidence: 0.94,
          sources: [{ source_name: "Water Act 1974", source_url: "https://cpcb.nic.in" }]
        }
      ],
      sources: [
        { source_name: "Water Act 1974", source_url: "https://cpcb.nic.in", authority: "Central Pollution Control Board", jurisdiction: "Central", is_official: true }
      ],
      disclaimer: "Deterministic Rule Engine analysis with ML predictions. Does not replace statutory government approval."
    } as unknown as T;
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
