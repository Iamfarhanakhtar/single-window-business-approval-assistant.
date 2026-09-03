"use client";

import React, { useEffect, useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Card } from "@/components/ui/Card";
import { ApprovalCard } from "@/components/domain/ApprovalCard";
import { LoadingState } from "@/components/ui/LoadingState";
import { approvalService } from "@/services/approvalService";
import { Approval } from "@/types";

export default function ApprovalsRoadmapPage() {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const list = await approvalService.getApprovals();
        setApprovals(list);
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
      <Sidebar role="entrepreneur" />
      <main className="flex-1 p-6 sm:p-8 space-y-6 max-w-7xl">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Customized Statutory Approvals Catalog</h1>
          <p className="text-xs text-slate-500">
            Applicable clearances for food processing & manufacturing units in Uttar Pradesh
          </p>
        </div>

        {isLoading ? (
          <LoadingState message="Loading statutory approval matrix..." />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {approvals.map((appr) => (
              <ApprovalCard key={appr.id} item={appr} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
