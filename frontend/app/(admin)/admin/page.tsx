"use client";

import React from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Card } from "@/components/ui/Card";
import { MetricCard } from "@/components/domain/MetricCard";
import { Users, Building2, BookOpen, ShieldAlert } from "lucide-react";

export default function AdminConsolePage() {
  return (
    <div className="flex min-h-[calc(100vh-4rem)] bg-slate-50">
      <Sidebar role="admin" />
      <main className="flex-1 p-6 sm:p-8 space-y-6 max-w-7xl">
        <div>
          <h1 className="text-xl font-bold text-slate-900">System Administration Console</h1>
          <p className="text-xs text-slate-500">Configure central/state acts, statutory departments, rules & user access</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Registered Users"
            value="5 Accounts"
            subtext="Demo roles configured"
            icon={<Users className="h-5 w-5 text-blue-600" />}
          />
          <MetricCard
            label="Active Departments"
            value="4 Agencies"
            subtext="UPPCB, Fire, FSSAI, Factories"
            icon={<Building2 className="h-5 w-5 text-emerald-600" />}
          />
          <MetricCard
            label="Regulatory Acts in KB"
            value="12 Acts"
            subtext="Indexed for RAG retrieval"
            icon={<BookOpen className="h-5 w-5 text-amber-600" />}
          />
          <MetricCard
            label="Audit Log Status"
            value="Active"
            subtext="Tamper-evident system logs"
            icon={<ShieldAlert className="h-5 w-5 text-purple-600" />}
          />
        </div>

        <Card title="System Environment & Foundation Details">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-700">
            <div className="rounded-lg bg-slate-50 p-4 space-y-2 border border-slate-200">
              <span className="font-semibold text-slate-900 block">FastAPI Backend Status:</span>
              <p>• Pydantic v2 validation contracts active</p>
              <p>• SQLAlchemy 2.0 ORM with 17 relational entities</p>
              <p>• JWT Bearer Authentication & RBAC protection</p>
              <p>• Deterministic 12-state workflow machine active</p>
            </div>
            <div className="rounded-lg bg-slate-50 p-4 space-y-2 border border-slate-200">
              <span className="font-semibold text-slate-900 block">AI/ML Foundation Status:</span>
              <p>• Strongly typed Python service interfaces ready</p>
              <p>• Rule Engine and Document AI pre-validation stubs active</p>
              <p>• ML delay predictor & feature definitions initialized</p>
              <p>• Synthetic training datasets loaded</p>
            </div>
          </div>
        </Card>
      </main>
    </div>
  );
}
