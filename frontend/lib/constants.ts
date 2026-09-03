/**
 * Design system semantics, navigation items, and test users
 */

export const STATUS_SEMANTICS = {
  // Green = completed/success
  APPROVED: { label: "Approved", bg: "bg-emerald-50 text-emerald-700 border-emerald-200", dot: "bg-emerald-500" },
  VALID: { label: "Valid", bg: "bg-emerald-50 text-emerald-700 border-emerald-200", dot: "bg-emerald-500" },
  COMPLETED: { label: "Completed", bg: "bg-emerald-50 text-emerald-700 border-emerald-200", dot: "bg-emerald-500" },
  RESOLVED: { label: "Resolved", bg: "bg-emerald-50 text-emerald-700 border-emerald-200", dot: "bg-emerald-500" },

  // Blue = processing/information
  UNDER_REVIEW: { label: "Under Review", bg: "bg-blue-50 text-blue-700 border-blue-200", dot: "bg-blue-500" },
  IN_REVIEW: { label: "In Review", bg: "bg-blue-50 text-blue-700 border-blue-200", dot: "bg-blue-500" },
  SUBMITTED: { label: "Submitted", bg: "bg-blue-50 text-blue-700 border-blue-200", dot: "bg-blue-500" },
  DOCUMENT_CHECK: { label: "Doc Pre-Check", bg: "bg-blue-50 text-blue-700 border-blue-200", dot: "bg-blue-500" },
  INSPECTION_SCHEDULED: { label: "Inspection Scheduled", bg: "bg-blue-50 text-blue-700 border-blue-200", dot: "bg-blue-500" },
  SCHEDULED: { label: "Scheduled", bg: "bg-blue-50 text-blue-700 border-blue-200", dot: "bg-blue-500" },

  // Yellow = action required/warning
  QUERY_RAISED: { label: "Query Raised", bg: "bg-amber-50 text-amber-700 border-amber-200", dot: "bg-amber-500" },
  OPEN: { label: "Action Required", bg: "bg-amber-50 text-amber-700 border-amber-200", dot: "bg-amber-500" },
  WARNING: { label: "Needs Attention", bg: "bg-amber-50 text-amber-700 border-amber-200", dot: "bg-amber-500" },
  INSPECTION_REQUIRED: { label: "Inspection Required", bg: "bg-amber-50 text-amber-700 border-amber-200", dot: "bg-amber-500" },

  // Red = rejected/error/SLA breach
  REJECTED: { label: "Rejected", bg: "bg-rose-50 text-rose-700 border-rose-200", dot: "bg-rose-500" },
  INVALID: { label: "Invalid Document", bg: "bg-rose-50 text-rose-700 border-rose-200", dot: "bg-rose-500" },
  BREACHED: { label: "SLA Breached", bg: "bg-rose-50 text-rose-700 border-rose-200", dot: "bg-rose-500" },

  // Gray = not started / draft
  DRAFT: { label: "Draft", bg: "bg-slate-100 text-slate-700 border-slate-200", dot: "bg-slate-400" },
  PENDING: { label: "Pending", bg: "bg-slate-100 text-slate-700 border-slate-200", dot: "bg-slate-400" },
  READY_FOR_SUBMISSION: { label: "Ready to Submit", bg: "bg-slate-100 text-slate-700 border-slate-200", dot: "bg-slate-400" },
  RENEWAL_MONITORING: { label: "Renewal Monitoring", bg: "bg-purple-50 text-purple-700 border-purple-200", dot: "bg-purple-500" },
};

export const DEMO_ACCOUNTS = [
  {
    role: "entrepreneur",
    label: "Entrepreneur (ABC Foods Pvt Ltd)",
    email: "entrepreneur@abcfoods.com",
    password: "password123",
    description: "Applicant managing industrial clearances, document uploads & SLA tracking."
  },
  {
    role: "government_officer",
    label: "Government Nodal Officer (District Magistrate)",
    email: "collector.ghaziabad@gov.in",
    password: "password123",
    description: "High-level oversight of inter-departmental performance, bottlenecks & SLA compliance."
  },
  {
    role: "department_officer",
    label: "Department Scrutiny Officer (UPPCB)",
    email: "officer.uppcb@gov.in",
    password: "password123",
    description: "Reviewing submissions, scheduling inspections, raising queries & issuing consent."
  },
  {
    role: "administrator",
    label: "System Administrator",
    email: "admin@gov.in",
    password: "password123",
    description: "Configuring regulations, single-window rules, departments and user access."
  }
];
