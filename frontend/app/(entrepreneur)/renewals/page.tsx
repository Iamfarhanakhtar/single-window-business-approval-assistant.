"use client";

import React, { useEffect, useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Card } from "@/components/ui/Card";
import { LoadingState } from "@/components/ui/LoadingState";
import { approvalService } from "@/services/approvalService";
import { Renewal } from "@/types";
import { RefreshCw, CalendarClock } from "lucide-react";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { formatDate } from "@/lib/utils";

export default function RenewalsPage() {
  const [renewals, setRenewals] = useState<Renewal[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const list = await approvalService.getRenewals();
        setRenewals(list);
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
      <main className="flex-1 p-6 sm:p-8 space-y-6 max-w-5xl">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Statutory License Renewals & Validity</h1>
          <p className="text-xs text-slate-500">Automated expiration tracking and renewal alerts</p>
        </div>

        {isLoading ? (
          <LoadingState message="Checking license validity timelines..." />
        ) : renewals.length > 0 ? (
          <div className="space-y-4">
            {renewals.map((r) => (
              <Card key={r.id}>
                <div className="flex items-center justify-between">
                  <div>
                    <span className="font-mono text-xs font-semibold text-blue-700">{r.approval_code}</span>
                    <h4 className="text-base font-semibold text-slate-900">License: {r.license_number}</h4>
                    <span className="text-xs text-slate-500">Expiry Date: {formatDate(r.expiry_date)}</span>
                  </div>
                  <StatusBadge status={r.is_renewed ? "APPROVED" : "UNDER_REVIEW"} />
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card>
            <div className="flex items-center gap-3 p-4 text-sm text-slate-600">
              <RefreshCw className="h-5 w-5 text-blue-600" />
              <span>All active licenses and NOCs are currently valid. Expiration tracking is active.</span>
            </div>
          </Card>
        )}
      </main>
    </div>
  );
}
