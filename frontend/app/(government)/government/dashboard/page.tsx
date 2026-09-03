"use client";

import React, { useEffect, useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { MetricCard } from "@/components/domain/MetricCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/LoadingState";
import { dashboardService } from "@/services/dashboardService";
import { applicationService } from "@/services/applicationService";
import { Application } from "@/types";
import {
  BarChart3,
  CheckCircle2,
  Clock,
  CalendarCheck2,
  AlertCircle,
  Building,
  TrendingUp,
  ShieldCheck
} from "lucide-react";

export default function GovernmentDashboard() {
  const [summary, setSummary] = useState<any>(null);
  const [analytics, setAnalytics] = useState<any>(null);
  const [applications, setApplications] = useState<Application[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [sum, ana, apps] = await Promise.all([
          dashboardService.getSummary(),
          dashboardService.getAnalytics(),
          applicationService.getApplications()
        ]);
        setSummary(sum);
        setAnalytics(ana);
        setApplications(apps);
      } catch (err) {
        console.error("Error loading government dashboard", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex">
        <Sidebar role="government" />
        <div className="flex-1 p-8">
          <LoadingState message="Aggregating inter-departmental compliance analytics..." />
        </div>
      </div>
    );
  }

  const columns = [
    {
      header: "Application #",
      accessorKey: "application_number" as keyof Application,
      cell: (app: Application) => <span className="font-mono font-semibold text-blue-700">{app.application_number}</span>
    },
    {
      header: "Status",
      accessorKey: "status" as keyof Application,
      cell: (app: Application) => <StatusBadge status={app.status} />
    },
    {
      header: "Active Clearances",
      cell: (app: Application) => (
        <span className="text-xs text-slate-600">
          {app.application_approvals.length} Departments
        </span>
      )
    },
    {
      header: "AI Delay Risk",
      cell: (app: Application) => (
        <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
          {Math.round(app.overall_risk_score * 100)}% (Low)
        </span>
      )
    },
    {
      header: "Created Date",
      cell: (app: Application) => <span className="text-xs text-slate-500">12 Feb 2026</span>
    }
  ];

  return (
    <div className="flex min-h-[calc(100vh-4rem)] bg-slate-50">
      <Sidebar role="government" />

      <main className="flex-1 p-6 sm:p-8 space-y-6 max-w-7xl">
        {/* Executive Header */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Building className="h-5 w-5 text-blue-700" />
              <h1 className="text-xl font-bold text-slate-900">Government Executive Oversight Portal</h1>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              District Single-Window Nodal Administration • Ghaziabad Industrial Region, Uttar Pradesh
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 border border-emerald-200 px-3 py-1 text-xs font-semibold text-emerald-700">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              Realtime State SLA Monitoring
            </span>
          </div>
        </div>

        {/* Executive KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Total Submissions"
            value="1"
            subtext="ABC Foods Pvt Ltd"
            icon={<BarChart3 className="h-5 w-5 text-blue-600" />}
          />
          <MetricCard
            label="SLA Compliance Rate"
            value="94.2%"
            subtext="+2.4% vs last quarter"
            trend={{ value: "Compliant", isPositive: true }}
            icon={<CheckCircle2 className="h-5 w-5 text-emerald-600" />}
          />
          <MetricCard
            label="Avg Clearance Time"
            value="21.4 Days"
            subtext="Target statutory SLA: 30 days"
            icon={<Clock className="h-5 w-5 text-amber-600" />}
          />
          <MetricCard
            label="Active Site Inspections"
            value="1 Visit"
            subtext="Joint UPPCB verification"
            icon={<CalendarCheck2 className="h-5 w-5 text-blue-600" />}
          />
        </div>

        {/* Department Clearance Performance Breakdown */}
        <Card title="Inter-Departmental SLA Efficiency" subtitle="Statutory clearance processing speed by agency">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-2">
            {analytics?.department_clearance_efficiency?.map((dept: any, idx: number) => (
              <div key={idx} className="rounded-lg border border-slate-200 bg-slate-50/50 p-4">
                <span className="text-xs font-mono font-bold text-blue-800">{dept.department}</span>
                <div className="mt-2 flex items-baseline justify-between">
                  <span className="text-lg font-bold text-slate-900">{dept.avg_days} Days</span>
                  <span className="text-xs text-slate-500">SLA: {dept.sla_target}d</span>
                </div>
                <div className="mt-2 text-xs font-semibold text-emerald-700">
                  {dept.compliance}% SLA Adherence
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* AI Bottleneck Advisory */}
        <Alert variant="warning" title="AI Regulatory Intelligence & Bottleneck Advisory">
          Analysis of recent industrial submissions indicates that <strong>34% of scrutiny delays</strong> stem from incomplete
          Effluent Treatment Plant (ETP) wastewater balance schematics. Automated pre-validation has been enabled to prevent submission of deficient filings.
        </Alert>

        {/* Applications Scrutiny Queue Table */}
        <Card title="Master Application Scrutiny Queue" subtitle="Real-time multi-departmental tracking">
          <DataTable
            columns={columns}
            data={applications}
            emptyMessage="No pending applications requiring scrutiny."
          />
        </Card>
      </main>
    </div>
  );
}
