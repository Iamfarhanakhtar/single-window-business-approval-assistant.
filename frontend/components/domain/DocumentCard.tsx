import React from "react";
import { DocumentItem } from "@/types";
import { StatusBadge } from "../ui/StatusBadge";
import { formatDate } from "@/lib/utils";
import { FileText, CheckCircle2, AlertTriangle, ShieldCheck } from "lucide-react";

export interface DocumentCardProps {
  doc: DocumentItem;
}

export const DocumentCard: React.FC<DocumentCardProps> = ({ doc }) => {
  const validationStatus = doc.validation?.status || (doc.is_verified ? "VALID" : "PENDING");

  return (
    <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:border-slate-300">
      <div className="flex items-center gap-3.5">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-700">
          <FileText className="h-5 w-5" />
        </div>
        <div>
          <h4 className="text-sm font-semibold text-slate-900">{doc.document_type}</h4>
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span>{doc.file_name}</span>
            <span>•</span>
            <span>{(doc.file_size_bytes / (1024 * 1024)).toFixed(2)} MB</span>
            <span>•</span>
            <span>Uploaded {formatDate(doc.uploaded_at)}</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {doc.is_reusable && (
          <span className="hidden sm:inline-flex items-center gap-1 rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
            <ShieldCheck className="h-3.5 w-3.5 text-slate-500" />
            Reusable
          </span>
        )}
        <StatusBadge status={validationStatus} />
      </div>
    </div>
  );
};
