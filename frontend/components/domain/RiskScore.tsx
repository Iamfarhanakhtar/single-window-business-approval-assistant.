import React from "react";
import { cn } from "@/lib/utils";
import { ShieldAlert, ShieldCheck, Shield } from "lucide-react";

export interface RiskScoreProps {
  score: number; // 0.0 to 1.0
  label?: string;
  className?: string;
}

export const RiskScore: React.FC<RiskScoreProps> = ({ score, label = "AI Compliance Risk Score", className }) => {
  const percentage = Math.round(score * 100);

  let riskLevel = "Low Risk";
  let colorStyle = "text-emerald-700 bg-emerald-50 border-emerald-200";
  let icon = <ShieldCheck className="h-5 w-5 text-emerald-600" />;

  if (score > 0.6) {
    riskLevel = "High Delay Probability";
    colorStyle = "text-rose-700 bg-rose-50 border-rose-200";
    icon = <ShieldAlert className="h-5 w-5 text-rose-600" />;
  } else if (score > 0.3) {
    riskLevel = "Moderate Scrutiny Risk";
    colorStyle = "text-amber-700 bg-amber-50 border-amber-200";
    icon = <Shield className="h-5 w-5 text-amber-600" />;
  }

  return (
    <div className={cn("rounded-xl border p-4 shadow-sm flex items-center justify-between", colorStyle, className)}>
      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-white/80 p-2 shadow-xs">{icon}</div>
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider opacity-80">{label}</span>
          <h4 className="text-sm font-bold tracking-tight">{riskLevel} ({percentage}%)</h4>
        </div>
      </div>
      <div className="text-right">
        <span className="text-xs font-medium opacity-75">AI Predictive Assessment</span>
      </div>
    </div>
  );
};
