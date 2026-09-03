import {
  User,
  AuthResponse,
  Department,
  Approval,
  Business,
  Application,
  DocumentItem,
  QueryRecord,
  Inspection,
  Renewal,
  Incentive,
  AnalyzeBusinessResponse
} from "@/types";

export const MOCK_USERS: Record<string, { user: User; auth: AuthResponse }> = {
  "entrepreneur@abcfoods.com": {
    user: {
      id: "usr-ent-001",
      email: "entrepreneur@abcfoods.com",
      full_name: "Rajesh Sharma",
      phone_number: "+91-9876543210",
      role: "entrepreneur",
      is_active: true,
      created_at: new Date().toISOString()
    },
    auth: {
      access_token: "mock-jwt-token-entrepreneur",
      token_type: "bearer",
      role: "entrepreneur",
      user_id: "usr-ent-001",
      email: "entrepreneur@abcfoods.com",
      full_name: "Rajesh Sharma"
    }
  },
  "collector.ghaziabad@gov.in": {
    user: {
      id: "usr-gov-001",
      email: "collector.ghaziabad@gov.in",
      full_name: "IAS S. K. Awasthi (District Magistrate / Nodal Officer)",
      phone_number: "+91-9833445566",
      role: "government_officer",
      is_active: true,
      created_at: new Date().toISOString()
    },
    auth: {
      access_token: "mock-jwt-token-government-officer",
      token_type: "bearer",
      role: "government_officer",
      user_id: "usr-gov-001",
      email: "collector.ghaziabad@gov.in",
      full_name: "IAS S. K. Awasthi (District Magistrate / Nodal Officer)"
    }
  },
  "officer.uppcb@gov.in": {
    user: {
      id: "usr-dept-001",
      email: "officer.uppcb@gov.in",
      full_name: "Dr. Alok Verma",
      phone_number: "+91-9811223344",
      role: "department_officer",
      department_id: "dept-uppcb",
      is_active: true,
      created_at: new Date().toISOString()
    },
    auth: {
      access_token: "mock-jwt-token-department-officer",
      token_type: "bearer",
      role: "department_officer",
      user_id: "usr-dept-001",
      email: "officer.uppcb@gov.in",
      full_name: "Dr. Alok Verma"
    }
  },
  "admin@gov.in": {
    user: {
      id: "usr-adm-001",
      email: "admin@gov.in",
      full_name: "Chief System Administrator",
      phone_number: "+91-9899887766",
      role: "administrator",
      is_active: true,
      created_at: new Date().toISOString()
    },
    auth: {
      access_token: "mock-jwt-token-administrator",
      token_type: "bearer",
      role: "administrator",
      user_id: "usr-adm-001",
      email: "admin@gov.in",
      full_name: "Chief System Administrator"
    }
  }
};

export const MOCK_DEPARTMENTS: Department[] = [
  {
    id: "dept-uppcb",
    code: "UPPCB",
    name: "Uttar Pradesh Pollution Control Board",
    state: "Uttar Pradesh",
    description: "Statutory authority for industrial environmental consents (Air/Water Acts)",
    sla_default_days: 30,
    is_active: true
  },
  {
    id: "dept-fire",
    code: "FIRE_DEPT",
    name: "State Fire Prevention & Emergency Services",
    state: "Uttar Pradesh",
    description: "Fire safety compliance and structural NOC issuance",
    sla_default_days: 15,
    is_active: true
  },
  {
    id: "dept-fssai",
    code: "FSSAI",
    name: "Food Safety & Standards Authority of India",
    state: "Central / UP State",
    description: "Food manufacturing and hygiene safety licensing",
    sla_default_days: 21,
    is_active: true
  },
  {
    id: "dept-factories",
    code: "FACTORIES_DEPT",
    name: "Directorate of Factories & Boilers",
    state: "Uttar Pradesh",
    description: "Factory registration, worker safety, and building plan clearance",
    sla_default_days: 20,
    is_active: true
  }
];

export const MOCK_APPROVALS: Approval[] = [
  {
    id: "appr-fire",
    code: "FIRE_NOC",
    name: "Fire Safety No Objection Certificate (Form-B)",
    category: "Safety",
    description: "Mandatory clearance for commercial & manufacturing units",
    sla_days: 15,
    validity_years: 3,
    statutory_fee: 5000,
    requires_inspection: true,
    department_id: "dept-fire",
    requirements: [
      {
        id: "req-1",
        document_type: "Building Layout & Evacuation Plan",
        is_mandatory: true,
        description: "Certified structural blueprint indicating emergency exits and hydrant placement"
      }
    ]
  },
  {
    id: "appr-pcb",
    code: "PCB_CTE",
    name: "Consent to Establish (Orange Category - Food Industry)",
    category: "Environmental",
    description: "Pollution control clearance under Water & Air Acts",
    sla_days: 30,
    validity_years: 5,
    statutory_fee: 25000,
    requires_inspection: true,
    department_id: "dept-uppcb",
    requirements: [
      {
        id: "req-2",
        document_type: "Effluent Treatment Plant (ETP) Scheme",
        is_mandatory: true,
        description: "Detailed wastewater treatment and water balance calculation"
      }
    ]
  },
  {
    id: "appr-fssai",
    code: "FSSAI_MFG",
    name: "FSSAI State Manufacturing License",
    category: "Operational",
    description: "Statutory food safety manufacturing compliance",
    sla_days: 21,
    validity_years: 5,
    statutory_fee: 7500,
    requires_inspection: false,
    department_id: "dept-fssai",
    requirements: [
      {
        id: "req-3",
        document_type: "FSMS Blueprint & Potability Report",
        is_mandatory: true,
        description: "Food Safety Management System layout and certified laboratory water analysis"
      }
    ]
  },
  {
    id: "appr-factories",
    code: "FACTORY_LIC",
    name: "Factory License & Structural Registration",
    category: "Labor & Safety",
    description: "Factories Act 1948 Section 6 clearance",
    sla_days: 20,
    validity_years: 1,
    statutory_fee: 10000,
    requires_inspection: true,
    department_id: "dept-factories",
    requirements: [
      {
        id: "req-4",
        document_type: "Factory Architectural Plan & Machinery Layout",
        is_mandatory: true,
        description: "Detailed machinery layout signed by certified chartered engineer"
      }
    ]
  }
];

export const MOCK_BUSINESSES: Business[] = [
  {
    id: "biz-001",
    user_id: "usr-ent-001",
    legal_name: "ABC Foods Private Limited",
    trade_name: "ABC Organics",
    registration_type: "Private Limited Company",
    pan_number: "AAACA1234F",
    gstin: "09AAACA1234F1Z5",
    created_at: new Date(Date.now() - 30 * 86400000).toISOString(),
    profile: {
      id: "prof-001",
      business_id: "biz-001",
      sector: "Food Processing",
      sub_sector: "Organic Grain & Snack Processing",
      state: "Uttar Pradesh",
      district: "Ghaziabad",
      address: "Plot No. 42-B, Sahibabad Industrial Area, Site IV",
      pincode: "201010",
      investment_amount: 50000000,
      employee_count: 80,
      built_up_area_sqm: 3200,
      power_requirement_kw: 150,
      water_requirement_kld: 25,
      hazardous_materials: false,
      details: { cold_storage_facility: true, boiler_installed: false },
      updated_at: new Date(Date.now() - 25 * 86400000).toISOString()
    }
  }
];

export const MOCK_APPLICATIONS: Application[] = [
  {
    id: "app-001",
    application_number: "APP-2026-UP-0042",
    business_id: "biz-001",
    status: "UNDER_REVIEW",
    submission_date: new Date(Date.now() - 12 * 86400000).toISOString(),
    estimated_completion_date: new Date(Date.now() + 18 * 86400000).toISOString(),
    overall_risk_score: 0.22,
    created_at: new Date(Date.now() - 14 * 86400000).toISOString(),
    updated_at: new Date(Date.now() - 2 * 86400000).toISOString(),
    application_approvals: [
      {
        id: "aa-1",
        approval_id: "appr-fire",
        status: "APPROVED",
        sla_target_date: new Date(Date.now() + 3 * 86400000).toISOString(),
        decision_date: new Date(Date.now() - 2 * 86400000).toISOString(),
        decision_remarks: "Site inspection verified. All hydrant points and fire barriers fully compliant.",
        certificate_number: "UP-FIRE-2026-9812",
        approval: MOCK_APPROVALS[0]
      },
      {
        id: "aa-2",
        approval_id: "appr-pcb",
        status: "QUERY_RAISED",
        sla_target_date: new Date(Date.now() + 8 * 86400000).toISOString(),
        approval: MOCK_APPROVALS[1]
      },
      {
        id: "aa-3",
        approval_id: "appr-fssai",
        status: "IN_REVIEW",
        sla_target_date: new Date(Date.now() + 9 * 86400000).toISOString(),
        approval: MOCK_APPROVALS[2]
      },
      {
        id: "aa-4",
        approval_id: "appr-factories",
        status: "INSPECTION_SCHEDULED",
        sla_target_date: new Date(Date.now() + 10 * 86400000).toISOString(),
        approval: MOCK_APPROVALS[3]
      }
    ]
  }
];

export const MOCK_DOCUMENTS: DocumentItem[] = [
  {
    id: "doc-1",
    business_id: "biz-001",
    application_id: "app-001",
    document_type: "Building Layout & Evacuation Plan",
    file_name: "ABC_Foods_Site_Layout_Approved.pdf",
    file_size_bytes: 2450000,
    mime_type: "application/pdf",
    is_verified: true,
    is_reusable: true,
    uploaded_at: new Date(Date.now() - 13 * 86400000).toISOString(),
    validation: {
      id: "val-1",
      status: "VALID",
      validation_score: 0.96,
      issues_detected: [],
      validated_at: new Date(Date.now() - 13 * 86400000).toISOString()
    }
  },
  {
    id: "doc-2",
    business_id: "biz-001",
    application_id: "app-001",
    document_type: "Effluent Treatment Plant (ETP) Scheme",
    file_name: "ETP_Design_25KLD_Ghaziabad.pdf",
    file_size_bytes: 3820000,
    mime_type: "application/pdf",
    is_verified: false,
    is_reusable: false,
    uploaded_at: new Date(Date.now() - 13 * 86400000).toISOString(),
    validation: {
      id: "val-2",
      status: "WARNING",
      validation_score: 0.74,
      issues_detected: ["Discharge parameters require clarification under CPCB Norms Schedule VI"],
      validated_at: new Date(Date.now() - 12 * 86400000).toISOString()
    }
  },
  {
    id: "doc-3",
    business_id: "biz-001",
    application_id: "app-001",
    document_type: "FSMS Blueprint & Potability Report",
    file_name: "FSMS_Certificate_Water_Test.pdf",
    file_size_bytes: 1890000,
    mime_type: "application/pdf",
    is_verified: true,
    is_reusable: true,
    uploaded_at: new Date(Date.now() - 13 * 86400000).toISOString(),
    validation: {
      id: "val-3",
      status: "VALID",
      validation_score: 0.98,
      issues_detected: [],
      validated_at: new Date(Date.now() - 13 * 86400000).toISOString()
    }
  }
];

export const MOCK_QUERIES: QueryRecord[] = [
  {
    id: "query-1",
    application_id: "app-001",
    raised_by_id: "usr-dept-001",
    department_code: "UPPCB",
    query_text: "Please submit updated daily chemical dosing balance chart for the secondary clarification chamber of the 25 KLD ETP unit.",
    status: "OPEN",
    raised_at: new Date(Date.now() - 2 * 86400000).toISOString()
  }
];

export const MOCK_INSPECTIONS: Inspection[] = [
  {
    id: "insp-1",
    application_id: "app-001",
    department_id: "dept-factories",
    scheduled_date: new Date(Date.now() + 4 * 86400000).toISOString(),
    status: "SCHEDULED",
    remarks: "Joint structural safety and worker ventilation verification on factory floor.",
    created_at: new Date(Date.now() - 3 * 86400000).toISOString()
  }
];

export const MOCK_RENEWALS: Renewal[] = [
  {
    id: "ren-1",
    business_id: "biz-001",
    approval_code: "FIRE_NOC",
    license_number: "UP-FIRE-2026-9812",
    expiry_date: new Date(Date.now() + 365 * 86400000).toISOString(),
    is_renewed: false
  },
  {
    id: "ren-2",
    business_id: "biz-001",
    approval_code: "FSSAI_MFG",
    license_number: "FSSAI-UP-10022026-004",
    expiry_date: new Date(Date.now() + 730 * 86400000).toISOString(),
    is_renewed: true
  }
];

export const MOCK_INCENTIVES: Incentive[] = [
  {
    id: "inc-1",
    scheme_name: "UP Food Processing Industry Policy - Capital Investment Subsidy",
    authority: "Department of Horticulture & Food Processing, Govt of UP",
    eligible_sectors: ["Food Processing", "Agri-Business", "Cold Chain"],
    min_investment: 10000000,
    max_subsidy_amount: 5000000,
    subsidy_percentage: 25,
    description: "Direct capital grant of up to 25% on plant and machinery for newly established food processing facilities in Uttar Pradesh.",
    portal_link: "https://up.gov.in"
  },
  {
    id: "inc-2",
    scheme_name: "MSME Interest Subvention & Power Tariff Exemption Scheme",
    authority: "Directorate of Industries, Uttar Pradesh",
    eligible_sectors: ["Manufacturing", "Food Processing", "Textiles"],
    min_investment: 5000000,
    max_subsidy_amount: 2000000,
    subsidy_percentage: 5,
    description: "5% annual interest subvention on term loans and 100% stamp duty exemption on industrial land registered in Sahibabad industrial region.",
    portal_link: "https://msme.up.gov.in"
  }
];

export const MOCK_ANALYTICS = {
  monthly_applications: [
    { month: "Jan", count: 42 },
    { month: "Feb", count: 58 },
    { month: "Mar", count: 65 },
    { month: "Apr", count: 78 },
    { month: "May", count: 92 },
    { month: "Jun", count: 110 }
  ],
  department_clearance_efficiency: [
    { department: "UPPCB", avg_days: 24, sla_target: 30, compliance: 92.5 },
    { department: "FIRE_DEPT", avg_days: 11, sla_target: 15, compliance: 96.0 },
    { department: "FSSAI", avg_days: 18, sla_target: 21, compliance: 91.2 },
    { department: "FACTORIES_DEPT", avg_days: 16, sla_target: 20, compliance: 94.8 }
  ],
  bottlenecks: [
    { factor: "Missing ETP schematics in initial submission", affected_percentage: 34 },
    { factor: "Delayed joint site inspection slot booking", affected_percentage: 22 },
    { factor: "Structural stability certificate resubmissions", affected_percentage: 14 }
  ]
};

export const MOCK_AI_ANALYSIS: AnalyzeBusinessResponse = {
  applicable_approvals: [
    {
      code: "PCB_CTE",
      name: "Consent to Establish (Orange Category)",
      department: "UPPCB",
      category: "Environmental",
      sla_days: 30,
      fee: 25000,
      mandatory: true,
      prerequisites: ["ETP Schematic", "Water Balance"]
    },
    {
      code: "FIRE_NOC",
      name: "Fire Safety Clearance (Form-B)",
      department: "Fire Department",
      category: "Safety",
      sla_days: 15,
      fee: 5000,
      mandatory: true,
      prerequisites: ["Evacuation Plan"]
    },
    {
      code: "FSSAI_MFG",
      name: "Food Manufacturing License",
      department: "FSSAI",
      category: "Operational",
      sla_days: 21,
      fee: 7500,
      mandatory: true,
      prerequisites: ["FSMS Blueprint"]
    }
  ],
  required_documents: [
    "Building Layout & Evacuation Plan",
    "Effluent Treatment Plant (ETP) Scheme",
    "FSMS Blueprint & Potability Report",
    "Chartered Engineer Structural Certificate"
  ],
  risk_score: 0.22,
  delay_probability: 0.18,
  predicted_processing_days: 28,
  eligible_incentives: [
    "UP Food Processing Industry Policy - Capital Subsidy (25%)",
    "MSME 5% Interest Subvention Scheme"
  ],
  explanation: "Entity is classified under Food Processing (Orange Category) in Ghaziabad, UP. Parallel processing recommended across UPPCB, Fire, and FSSAI to achieve clearance within standard statutory SLA of 30 days."
};
