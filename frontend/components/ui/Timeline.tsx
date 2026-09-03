import React from "react";
import { cn } from "@/lib/utils";
import { Check, Clock, AlertCircle, Circle } from "lucide-react";

export interface TimelineStep {
  title: string;
  description?: string;
  status: "completed" | "current" | "upcoming" | "error";
  date?: string;
}

export interface TimelineProps {
  steps: TimelineStep[];
  className?: string;
}

export const Timeline: React.FC<TimelineProps> = ({ steps, className }) => {
  return (
    <div className={cn("space-y-4", className)}>
      {steps.map((step, idx) => {
        const isLast = idx === steps.length - 1;

        return (
          <div key={idx} className="relative flex gap-4">
            {!isLast && (
              <span
                className={cn(
                  "absolute left-4 top-8 -ml-px h-[calc(100%-8px)] w-0.5",
                  step.status === "completed" ? "bg-emerald-500" : "bg-slate-200"
                )}
                aria-hidden="true"
              />
            )}
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border">
              {step.status === "completed" && (
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-600 text-white">
                  <Check className="h-4 w-4 stroke-[3]" />
                </span>
              )}
              {step.status === "current" && (
                <span className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-blue-600 bg-white text-blue-600">
                  <Clock className="h-4 w-4 animate-pulse" />
                </span>
              )}
              {step.status === "upcoming" && (
                <span className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-slate-200 bg-white text-slate-300">
                  <Circle className="h-3 w-3" />
                </span>
              )}
              {step.status === "error" && (
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-rose-600 text-white">
                  <AlertCircle className="h-4 w-4" />
                </span>
              )}
            </div>
            <div className="flex-1 pt-1 pb-3">
              <div className="flex items-center justify-between">
                <p className={cn("text-sm font-semibold", step.status === "current" ? "text-blue-700" : "text-slate-900")}>
                  {step.title}
                </p>
                {step.date && <span className="text-xs text-slate-400">{step.date}</span>}
              </div>
              {step.description && <p className="mt-0.5 text-xs text-slate-500">{step.description}</p>}
            </div>
          </div>
        );
      })}
    </div>
  );
};
