"use client";

import React, { useEffect, useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { MetricCard } from "@/components/domain/MetricCard";
import { ApprovalCard } from "@/components/domain/ApprovalCard";
import { DocumentCard } from "@/components/domain/DocumentCard";
import { RiskScore } from "@/components/domain/RiskScore";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/LoadingState";
import { applicationService } from "@/services/applicationService";
import { Application, DocumentItem, QueryRecord, Inspection } from "@/types";
import {
  FolderKanban,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Upload,
  Calendar,
  Building2,
  Sparkles,
  ExternalLink
} from "lucide-react";
import { formatINR } from "@/lib/utils";

export default function EntrepreneurDashboard() {
  const [application, setApplication] = useState<Application | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [queries, setQueries] = useState<QueryRecord[]>([]);
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const apps = await applicationService.getApplications();
        if (apps && apps.length > 0) {
          const mainApp = apps[0];
          setApplication(mainApp);
          const docs = await applicationService.getDocuments(mainApp.id);
          const qList = await applicationService.getQueries(mainApp.id);
          const inspList = await applicationService.getInspections(mainApp.id);
          setDocuments(docs);
          setQueries(qList);
          setInspections(inspList);
        }
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex">
        <Sidebar role="entrepreneur" />
        <div className="flex-1 p-8">
          <LoadingState message="Loading your industrial clearance roadmap..." />
        </div>
      </div>
    );
  }

  const completedApprovals = application?.application_approvals.filter(a => a.status === "APPROVED").length || 0;
  const totalApprovals = application?.application_approvals.length || 4;
  const progressPercent = Math.round((completedApprovals / totalApprovals) * 100);

  return (
    <div className="flex min-h-[calc(100vh-4rem)] bg-slate-50">
      <Sidebar role="entrepreneur" />

      <main className="flex-1 p-6 sm:p-8 space-y-6 max-w-7xl">
        {/* Business Banner */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div>
            <div className="flex items-center gap-2">
              <Building2 className="h-5 w-5 text-blue-700" />
              <h1 className="text-xl font-bold text-slate-900">ABC Foods Private Limited</h1>
              <span className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-600 font-mono">
                CIN: U15400UP2026PTC123456
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Food Processing • Sahibabad Industrial Area, Ghaziabad, Uttar Pradesh • Investment: ₹5.00 Cr (80 Employees)
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm" className="flex items-center gap-1.5">
              <Upload className="h-3.5 w-3.5" /> Upload Document
            </Button>
            <Button size="sm" className="flex items-center gap-1.5">
              <Sparkles className="h-3.5 w-3.5" /> AI Roadmap Scan
            </Button>
          </div>
        </div>

        {/* Master Application Overview Card */}
        {application && (
          <Card className="p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Master Application Reference
                </span>
                <div className="mt-1 flex items-center gap-3">
                  <h2 className="text-lg font-bold text-slate-900">{application.application_number}</h2>
                  <StatusBadge status={application.status} />
                </div>
              </div>
              <div className="flex items-center gap-6 text-xs text-slate-600">
                <div>
                  <span className="text-slate-400 block">Submitted On</span>
                  <span className="font-semibold text-slate-800">12 Feb 2026</span>
                </div>
                <div>
                  <span className="text-slate-400 block">Target SLA Completion</span>
                  <span className="font-semibold text-slate-800">14 Mar 2026 (18 Days Left)</span>
                </div>
              </div>
            </div>

            <div className="mt-4 space-y-2">
              <ProgressBar
                value={progressPercent}
                label={`Overall Clearance Progress (${completedApprovals} of ${totalApprovals} Approvals Granted)`}
                color="emerald"
              />
            </div>
          </Card>
        )}

        {/* Metric Cards Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Total Clearances"
            value="4 Approvals"
            subtext="Running in parallel"
            icon={<FolderKanban className="h-5 w-5" />}
          />
          <MetricCard
            label="Approvals Granted"
            value={`${completedApprovals} / ${totalApprovals}`}
            subtext="Fire NOC Issued"
            icon={<CheckCircle2 className="h-5 w-5 text-emerald-600" />}
          />
          <MetricCard
            label="Active Site Inspections"
            value="1 Scheduled"
            subtext="Joint UPPCB site visit"
            icon={<Calendar className="h-5 w-5 text-blue-600" />}
          />
          <MetricCard
            label="Pending Queries"
            value="0 Open"
            subtext="All inquiries resolved"
            icon={<AlertTriangle className="h-5 w-5 text-emerald-600" />}
          />
        </div>

        {/* AI Regulatory Risk & Delay Assessment */}
        <RiskScore
          score={application?.overall_risk_score || 0.22}
          label="AI Regulatory Intelligence & Bottleneck Risk"
        />

        {/* Parallel Departmental Clearances Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-slate-900">Parallel Departmental Workflows</h3>
              <p className="text-xs text-slate-500">
                Independent approvals progressing concurrently under single statutory application
              </p>
            </div>
            <span className="text-xs font-medium text-slate-400">4 Active Channels</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {application?.application_approvals.map((aa) => (
              <ApprovalCard key={aa.id} item={aa} />
            ))}
          </div>
        </div>

        {/* Document Pre-Validation & Vault Preview */}
        <Card title="Uploaded Documents & AI Pre-Validation Status" subtitle="Pre-screened against regulatory checklists">
          <div className="space-y-3">
            {documents.map((doc) => (
              <DocumentCard key={doc.id} doc={doc} />
            ))}
          </div>
        </Card>
      </main>
    </div>
  );
}
