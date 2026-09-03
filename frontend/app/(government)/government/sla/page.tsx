"use client";

import React, { useEffect, useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Card } from "@/components/ui/Card";
import { Alert } from "@/components/ui/Alert";
import { MetricCard } from "@/components/domain/MetricCard";
import { dashboardService } from "@/services/dashboardService";
import { LoadingState } from "@/components/ui/LoadingState";
import { Clock, ShieldAlert, CheckCircle2, TrendingUp } from "lucide-react";

export default function GovernmentSLAPage() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await dashboardService.getAnalytics();
        setAnalytics(res);
      } catch (e) {
        console.error(e);
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="flex min-h-[calc(100vh-4rem)] bg-slate-50">
      <Sidebar role="government" />
      <main className="flex-1 p-6 sm:p-8 space-y-6 max-w-7xl">
        <div>
          <h1 className="text-xl font-bold text-slate-900">SLA Compliance & Bottleneck Identification</h1>
          <p className="text-xs text-slate-500">Statutory timeline monitoring, escalation tracking, and root-cause analysis</p>
        </div>

        {isLoading ? (
          <LoadingState message="Calculating state SLA metrics..." />
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <MetricCard
                label="Statewide Compliance"
                value="94.2%"
                subtext="Within statutory deadline"
                trend={{ value: "Compliant", isPositive: true }}
                icon={<CheckCircle2 className="h-5 w-5 text-emerald-600" />}
              />
              <MetricCard
                label="Average Lead Time"
                value="21.4 Days"
                subtext="Statutory target: 30 days"
                icon={<Clock className="h-5 w-5 text-blue-600" />}
              />
              <MetricCard
                label="Active Escalations"
                value="0 Cases"
                subtext="Zero active breaches"
                icon={<ShieldAlert className="h-5 w-5 text-slate-400" />}
              />
            </div>

            <Card title="Root-Cause Delay Bottlenecks" subtitle="AI-identified operational impediments">
              <div className="space-y-3">
                {analytics?.bottlenecks?.map((b: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between rounded-lg border border-slate-200 bg-slate-50/60 p-4">
                    <span className="text-sm font-medium text-slate-800">{b.factor}</span>
                    <span className="rounded bg-amber-100 text-amber-800 font-semibold px-2 py-0.5 text-xs">
                      {b.affected_percentage}% of queries
                    </span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
}
