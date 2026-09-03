"use client";

import React, { useEffect, useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Card } from "@/components/ui/Card";
import { LoadingState } from "@/components/ui/LoadingState";
import { approvalService } from "@/services/approvalService";
import { Incentive } from "@/types";
import { Gift, ExternalLink, IndianRupee } from "lucide-react";
import { Button } from "@/components/ui/Button";

export default function IncentivesPage() {
  const [incentives, setIncentives] = useState<Incentive[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const list = await approvalService.getIncentives();
        setIncentives(list);
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
          <h1 className="text-xl font-bold text-slate-900">State & Central Industrial Incentives</h1>
          <p className="text-xs text-slate-500">
            Subsidies and capital support schemes matched to your sector and investment profile
          </p>
        </div>

        {isLoading ? (
          <LoadingState message="Matching state industrial policy schemes..." />
        ) : (
          <div className="space-y-4">
            {incentives.map((inc) => (
              <Card key={inc.id} title={inc.scheme_name} subtitle={`Authority: ${inc.authority}`}>
                <p className="text-sm text-slate-700 leading-relaxed">{inc.description}</p>
                <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3 text-xs">
                  <div className="flex items-center gap-4 text-slate-600">
                    <span>Capital Subsidy: <strong className="text-emerald-700">{inc.subsidy_percentage}%</strong></span>
                    <span>Max Grant: <strong className="text-slate-900">₹{(inc.max_subsidy_amount / 10000000).toFixed(2)} Cr</strong></span>
                  </div>
                  {inc.portal_link && (
                    <a href={inc.portal_link} target="_blank" rel="noreferrer">
                      <Button variant="outline" size="sm" className="flex items-center gap-1">
                        <span>Scheme Details</span>
                        <ExternalLink className="h-3.5 w-3.5" />
                      </Button>
                    </a>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
