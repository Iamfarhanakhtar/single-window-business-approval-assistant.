"use client";

import React, { useEffect, useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Card } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { LoadingState } from "@/components/ui/LoadingState";
import { applicationService } from "@/services/applicationService";
import { Inspection } from "@/types";
import { formatDate } from "@/lib/utils";

export default function GovernmentInspectionsPage() {
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const list = await applicationService.getInspections();
        setInspections(list);
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
      header: "Inspection Ref",
      accessorKey: "id" as keyof Inspection,
      cell: (i: Inspection) => <span className="font-mono text-xs">{i.id.substring(0, 8)}...</span>
    },
    {
      header: "Scheduled Date",
      accessorKey: "scheduled_date" as keyof Inspection,
      cell: (i: Inspection) => <span className="font-semibold text-xs text-slate-800">{formatDate(i.scheduled_date)}</span>
    },
    {
      header: "Status",
      accessorKey: "status" as keyof Inspection,
      cell: (i: Inspection) => <StatusBadge status={i.status} />
    },
    {
      header: "Remarks",
      accessorKey: "remarks" as keyof Inspection,
      cell: (i: Inspection) => <span className="text-xs text-slate-600">{i.remarks || "Joint site verification"}</span>
    }
  ];

  return (
    <div className="flex min-h-[calc(100vh-4rem)] bg-slate-50">
      <Sidebar role="government" />
      <main className="flex-1 p-6 sm:p-8 space-y-6 max-w-7xl">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Synchronized Site Inspections</h1>
          <p className="text-xs text-slate-500">Joint inter-agency site visits and physical compliance audits</p>
        </div>

        {isLoading ? (
          <LoadingState message="Loading inspection calendar..." />
        ) : (
          <Card>
            <DataTable columns={columns} data={inspections} emptyMessage="No site visits currently scheduled." />
          </Card>
        )}
      </main>
    </div>
  );
}
