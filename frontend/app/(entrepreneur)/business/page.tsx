"use client";

import React, { useEffect, useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Card } from "@/components/ui/Card";
import { approvalService } from "@/services/approvalService";
import { Business } from "@/types";
import { Building2, MapPin, IndianRupee, Users, Shield } from "lucide-react";
import { formatINR } from "@/lib/utils";
import { LoadingState } from "@/components/ui/LoadingState";

export default function BusinessProfilePage() {
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const list = await approvalService.getBusinesses();
        setBusinesses(list);
      } catch (e) {
        console.error(e);
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  const biz = businesses[0];

  return (
    <div className="flex min-h-[calc(100vh-4rem)] bg-slate-50">
      <Sidebar role="entrepreneur" />
      <main className="flex-1 p-6 sm:p-8 space-y-6 max-w-5xl">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Industrial Business Profile</h1>
          <p className="text-xs text-slate-500">Enterprise particulars and statutory registrations</p>
        </div>

        {isLoading ? (
          <LoadingState message="Loading business particulars..." />
        ) : biz ? (
          <Card title={biz.legal_name} subtitle={`Registration: ${biz.registration_type}`}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
              <div className="space-y-3">
                <div>
                  <span className="text-xs text-slate-400 block">Trade Name</span>
                  <span className="font-semibold text-slate-800">{biz.trade_name || biz.legal_name}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-400 block">PAN Number</span>
                  <span className="font-mono font-semibold text-slate-800">{biz.pan_number || "AAACA1234F"}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-400 block">GSTIN</span>
                  <span className="font-mono font-semibold text-slate-800">{biz.gstin || "09AAACA1234F1Z5"}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-400 block">Sector</span>
                  <span className="font-semibold text-blue-700">{biz.profile?.sector || "Food Processing"}</span>
                </div>
              </div>

              <div className="space-y-3">
                <div>
                  <span className="text-xs text-slate-400 block">Location & District</span>
                  <span className="font-semibold text-slate-800">
                    {biz.profile?.district || "Ghaziabad"}, {biz.profile?.state || "Uttar Pradesh"}
                  </span>
                </div>
                <div>
                  <span className="text-xs text-slate-400 block">Capital Investment</span>
                  <span className="font-semibold text-emerald-700">{formatINR(biz.profile?.investment_amount || 50000000)}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-400 block">Workforce Count</span>
                  <span className="font-semibold text-slate-800">{biz.profile?.employee_count || 80} Employees</span>
                </div>
                <div>
                  <span className="text-xs text-slate-400 block">Hazardous Materials</span>
                  <span className="font-semibold text-slate-800">{biz.profile?.hazardous_materials ? "Yes" : "No"}</span>
                </div>
              </div>
            </div>
          </Card>
        ) : (
          <p className="text-sm text-slate-500">No business profile configured yet.</p>
        )}
      </main>
    </div>
  );
}
