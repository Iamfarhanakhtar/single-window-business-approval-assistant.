import React from "react";
import { Approval, ApplicationApproval } from "@/types";
import { StatusBadge } from "../ui/StatusBadge";
import { formatINR, formatDate } from "@/lib/utils";
import { Clock, ShieldCheck, FileCheck } from "lucide-react";

export interface ApprovalCardProps {
  item: ApplicationApproval | Approval;
  status?: string;
  onAction?: () => void;
}

export const ApprovalCard: React.FC<ApprovalCardProps> = ({ item, status, onAction }) => {
  const isAppApproval = "approval_id" in item;
  const approvalData = isAppApproval ? (item as ApplicationApproval).approval : (item as Approval);
  const currentStatus = status || (isAppApproval ? (item as ApplicationApproval).status : (approvalData?.verification_status || "PENDING"));

  const title = approvalData?.approval_name || approvalData?.name || "Statutory Approval";
  const code = approvalData?.id || approvalData?.code || "APPR";
  const authority = approvalData?.issuing_authority || approvalData?.description || "Regulatory Authority";
  const category = approvalData?.category || approvalData?.source_type;

  return (
    <div className="flex flex-col justify-between rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-slate-300">
      <div>
        <div className="flex items-start justify-between gap-2">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded">
                {code}
              </span>
              {category && (
                <span className="text-[10px] font-medium text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                  {category}
                </span>
              )}
            </div>
            <h4 className="mt-2 text-base font-semibold text-slate-900 leading-snug">
              {title}
            </h4>
          </div>
          <StatusBadge status={currentStatus} />
        </div>

        <p className="mt-2 text-xs text-slate-600 line-clamp-2">
          {authority}
        </p>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600">
        <div className="flex items-center gap-1">
          <Clock className="h-3.5 w-3.5 text-slate-400" />
          <span>{approvalData?.state ? `${approvalData.state}` : `SLA: ${approvalData?.sla_days || 15} days`}</span>
        </div>
        {approvalData?.source_name && (
          <div className="flex items-center gap-1 text-[11px] text-slate-500 font-medium">
            <span>{approvalData.source_name}</span>
          </div>
        )}
      </div>
    </div>
  );
};
