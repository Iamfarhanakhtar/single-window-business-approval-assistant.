"use client";

import React, { useEffect, useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Card } from "@/components/ui/Card";
import { dashboardService } from "@/services/dashboardService";
import { LoadingState } from "@/components/ui/LoadingState";
import { BarChart3, TrendingUp, Layers } from "lucide-react";

export default function GovernmentAnalyticsPage() {
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
          <h1 className="text-xl font-bold text-slate-900">State Industrial Analytics & Inflow Trends</h1>
          <p className="text-xs text-slate-500">Submission volumes, department clearance times, and regional compliance patterns</p>
        </div>

        {isLoading ? (
          <LoadingState message="Loading state analytics engine..." />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card title="Monthly Industrial Clearance Volume" subtitle="Filings submitted in 2026">
              <div className="h-48 flex items-end justify-between gap-3 pt-8 pb-2">
                {analytics?.monthly_applications?.map((m: any, idx: number) => {
                  const heightPercent = Math.round((m.count / 120) * 100);
                  return (
                    <div key={idx} className="flex-1 flex flex-col items-center gap-2">
                      <span className="text-xs font-bold text-slate-700">{m.count}</span>
                      <div
                        className="w-full rounded-t-md bg-blue-600 transition-all hover:bg-blue-700"
                        style={{ height: `${heightPercent}%` }}
                      />
                      <span className="text-xs text-slate-500">{m.month}</span>
                    </div>
                  );
                })}
              </div>
            </Card>

            <Card title="Departmental Efficiency Index" subtitle="Adherence against statutory SLA targets">
              <div className="space-y-4 pt-2">
                {analytics?.department_clearance_efficiency?.map((d: any, idx: number) => (
                  <div key={idx} className="space-y-1.5">
                    <div className="flex justify-between text-xs font-semibold">
                      <span className="text-slate-800">{d.department}</span>
                      <span className="text-emerald-700">{d.compliance}% on-time ({d.avg_days} / {d.sla_target} days)</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                      <div
                        className="h-full bg-emerald-600 rounded-full"
                        style={{ width: `${d.compliance}%` }}
                      />
                    </div>
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
