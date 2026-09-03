"use client";

import React, { useEffect, useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { LoadingState } from "@/components/ui/LoadingState";
import { applicationService } from "@/services/applicationService";
import { Application } from "@/types";

export default function GovernmentApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const list = await applicationService.getApplications();
        setApplications(list);
      } catch (e) {
        console.error(e);
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

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
      header: "Clearances In-Flight",
      cell: (app: Application) => (
        <span className="text-xs text-slate-600">
          {app.application_approvals.length} Departments
        </span>
      )
    },
    {
      header: "Risk Score",
      cell: (app: Application) => (
        <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
          {Math.round(app.overall_risk_score * 100)}% (Low)
        </span>
      )
    }
  ];

  return (
    <div className="flex min-h-[calc(100vh-4rem)] bg-slate-50">
      <Sidebar role="government" />
      <main className="flex-1 p-6 sm:p-8 space-y-6 max-w-7xl">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Application Scrutiny & Clearance Queue</h1>
          <p className="text-xs text-slate-500">Cross-departmental filings awaiting document review, inspection, or decision</p>
        </div>

        {isLoading ? (
          <LoadingState message="Loading scrutiny queue..." />
        ) : (
          <Card>
            <DataTable columns={columns} data={applications} emptyMessage="No applications currently under review." />
          </Card>
        )}
      </main>
    </div>
  );
}
