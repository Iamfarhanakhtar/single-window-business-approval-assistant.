/**
 * TypeScript Data Contracts for Bharat Compliance Platform (SIH-130)
 * Synchronized with FastAPI Pydantic Schemas
 */

export type UserRole = "entrepreneur" | "government_officer" | "department_officer" | "administrator";

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone_number?: string;
  role: UserRole;
  department_id?: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  role: UserRole;
  user_id: string;
  email: string;
  full_name: string;
}

export interface BusinessProfile {
  id: string;
  business_id: string;
  sector: string;
  sub_sector?: string;
  state: string;
  district: string;
  address?: string;
  pincode?: string;
  investment_amount: number;
  employee_count: number;
  built_up_area_sqm?: number;
  power_requirement_kw?: number;
  water_requirement_kld?: number;
  hazardous_materials: boolean;
  details?: Record<string, any>;
  updated_at: string;
}

export interface Business {
  id: string;
  user_id: string;
  legal_name: string;
  trade_name?: string;
  registration_type: string;
  pan_number?: string;
  gstin?: string;
  created_at: string;
  profile?: BusinessProfile;
}

export interface ApprovalRequirement {
  id: string;
  document_type: string;
  is_mandatory: boolean;
  description?: string;
}

export interface Approval {
  id: string;
  code: string;
  name: string;
  category?: string;
  description?: string;
  sla_days: number;
  validity_years: number;
  statutory_fee: number;
  requires_inspection: boolean;
  department_id: string;
  requirements?: ApprovalRequirement[];
}

export interface Department {
  id: string;
  code: string;
  name: string;
  state?: string;
  description?: string;
  sla_default_days: number;
  is_active: boolean;
  approvals?: Approval[];
}

export type ApplicationStatus =
  | "DRAFT"
  | "DOCUMENT_CHECK"
  | "READY_FOR_SUBMISSION"
  | "SUBMITTED"
  | "UNDER_REVIEW"
  | "INSPECTION_REQUIRED"
  | "INSPECTION_SCHEDULED"
  | "INSPECTION_COMPLETED"
  | "QUERY_RAISED"
  | "RESUBMITTED"
  | "APPROVED"
  | "REJECTED"
  | "RENEWAL_MONITORING";

export type ApprovalStatus =
  | "PENDING"
  | "IN_REVIEW"
  | "INSPECTION_SCHEDULED"
  | "QUERY_RAISED"
  | "APPROVED"
  | "REJECTED";

export interface ApplicationApproval {
  id: string;
  approval_id: string;
  status: ApprovalStatus;
  sla_target_date?: string;
  decision_date?: string;
  decision_remarks?: string;
  certificate_number?: string;
  approval?: Approval;
}

export interface Application {
  id: string;
  application_number: string;
  business_id: string;
  status: ApplicationStatus;
  submission_date?: string;
  estimated_completion_date?: string;
  overall_risk_score: number;
  created_at: string;
  updated_at: string;
  application_approvals: ApplicationApproval[];
}

export interface DocumentValidation {
  id: string;
  status: "PENDING" | "VALID" | "INVALID" | "WARNING";
  validation_score: number;
  extracted_metadata?: Record<string, any>;
  issues_detected?: string[];
  validated_at: string;
}

export interface DocumentItem {
  id: string;
  business_id: string;
  application_id?: string;
  document_type: string;
  file_name: string;
  file_size_bytes: number;
  mime_type: string;
  is_verified: boolean;
  is_reusable: boolean;
  uploaded_at: string;
  validation?: DocumentValidation;
}

export interface QueryRecord {
  id: string;
  application_id: string;
  raised_by_id: string;
  department_code: string;
  query_text: string;
  response_text?: string;
  status: "OPEN" | "RESPONDED" | "RESOLVED";
  raised_at: string;
  responded_at?: string;
}

export interface Inspection {
  id: string;
  application_id: string;
  department_id: string;
  scheduled_date: string;
  status: "SCHEDULED" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED";
  remarks?: string;
  created_at: string;
}

export interface Incentive {
  id: string;
  scheme_name: string;
  authority: string;
  eligible_sectors?: string[];
  min_investment: number;
  max_subsidy_amount: number;
  subsidy_percentage: number;
  description: string;
  portal_link?: string;
}

export interface Renewal {
  id: string;
  business_id: string;
  approval_code: string;
  license_number: string;
  expiry_date: string;
  reminder_sent_date?: string;
  is_renewed: boolean;
}

// AI/ML Service Contracts
export interface ApplicableApprovalItem {
  code: string;
  name: string;
  department: string;
  category: string;
  sla_days: number;
  fee: number;
  mandatory: boolean;
  prerequisites: string[];
}

export interface AnalyzeBusinessResponse {
  applicable_approvals: ApplicableApprovalItem[];
  required_documents: string[];
  risk_score: number;
  delay_probability: number;
  predicted_processing_days: number;
  eligible_incentives: string[];
  explanation: string;
}
