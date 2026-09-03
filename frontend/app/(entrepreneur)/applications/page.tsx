"use client";

import React, { useEffect, useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { LoadingState } from "@/components/ui/LoadingState";
import { applicationService } from "@/services/applicationService";
import { Application } from "@/types";

export default function ApplicationsPage() {
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
      header: "Application Number",
      accessorKey: "application_number" as keyof Application,
      cell: (a: Application) => <span className="font-mono font-bold text-blue-700">{a.application_number}</span>
    },
    {
      header: "Status",
      accessorKey: "status" as keyof Application,
      cell: (a: Application) => <StatusBadge status={a.status} />
    },
    {
      header: "Approvals Count",
      cell: (a: Application) => <span className="text-xs">{a.application_approvals.length} Clearances</span>
    },
    {
      header: "Delay Risk",
      cell: (a: Application) => (
        <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
          {Math.round(a.overall_risk_score * 100)}% (Low)
        </span>
      )
    },
    {
      header: "Submission Date",
      cell: (a: Application) => <span className="text-xs text-slate-500">12 Feb 2026</span>
    }
  ];

  return (
    <div className="flex min-h-[calc(100vh-4rem)] bg-slate-50">
      <Sidebar role="entrepreneur" />
      <main className="flex-1 p-6 sm:p-8 space-y-6 max-w-7xl">
        <div>
          <h1 className="text-xl font-bold text-slate-900">My Statutory Applications</h1>
          <p className="text-xs text-slate-500">Track clearance progress, parallel workflows & milestones</p>
        </div>

        {isLoading ? (
          <LoadingState message="Loading applications..." />
        ) : (
          <Card>
            <DataTable columns={columns} data={applications} emptyMessage="No applications submitted yet." />
          </Card>
        )}
      </main>
    </div>
  );
}
