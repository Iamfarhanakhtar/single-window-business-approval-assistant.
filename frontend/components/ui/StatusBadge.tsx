import React from "react";
import { cn } from "@/lib/utils";
import { STATUS_SEMANTICS } from "@/lib/constants";

export interface StatusBadgeProps {
  status: string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className }) => {
  const semantic = STATUS_SEMANTICS[status as keyof typeof STATUS_SEMANTICS] || {
    label: status.replace(/_/g, " "),
    bg: "bg-slate-100 text-slate-700 border-slate-200",
    dot: "bg-slate-400"
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-xs font-semibold uppercase tracking-wider",
        semantic.bg,
        className
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", semantic.dot)} />
      {semantic.label}
    </span>
  );
};
