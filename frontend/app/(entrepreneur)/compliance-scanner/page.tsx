"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { LoadingState } from "@/components/ui/LoadingState";
import { aiService, ComplianceAnalyzeParams } from "@/services/aiService";
import { UnifiedComplianceAnalysisResponse } from "@/types";
import { formatINR } from "@/lib/utils";
import {
  Sparkles,
  ShieldCheck,
  Clock,
  AlertTriangle,
  BookOpen,
  CheckCircle2,
  FileText,
  Building2,
  Zap,
  ArrowRight,
  ExternalLink,
  ShieldAlert
} from "lucide-react";

export default function ComplianceScannerPage() {
  const [formData, setFormData] = useState<ComplianceAnalyzeParams>({
    sector: "Food Processing",
    state: "Uttar Pradesh",
    district: "Ghaziabad",
    investment: 50000000,
    employees: 80,
    project_stage: "Pre-Operation",
    connected_load_kw: 150,
    has_boiler: true,
    is_food_business: true,
    water_requirement_kld: 25,
    hazardous_materials: false,
    built_up_area_sqm: 1200,
  });

  const [analysis, setAnalysis] = useState<UnifiedComplianceAnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunAnalysis = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const result = await aiService.analyzeCompliance(formData);
      setAnalysis(result);
    } catch (err: any) {
      console.error("Compliance analysis error", err);
      setError(err.message || "Failed to complete compliance scan.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)] bg-slate-50">
      <Sidebar role="entrepreneur" />

      <main className="flex-1 p-6 sm:p-8 space-y-6 max-w-7xl">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-blue-700" />
              <h1 className="text-xl font-bold text-slate-900">AI Compliance Roadmap & Risk Scanner</h1>
            </div>
            <p className="text-xs text-slate-500">
              Deterministic Rule Engine • ML Risk & Delay Forecasting • Statutory RAG Citations
            </p>
          </div>
        </div>

        {/* Input Parameters Form */}
        <Card title="Industrial Business Parameters" subtitle="Configure your enterprise profile to evaluate statutory obligations">
          <form onSubmit={handleRunAnalysis} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              <div>
                <label className="text-xs font-medium text-slate-700 block mb-1">State Jurisdiction</label>
                <select
                  value={formData.state}
                  onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                  className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                >
                  <option value="Uttar Pradesh">Uttar Pradesh</option>
                  <option value="Maharashtra">Maharashtra (Future)</option>
                  <option value="Gujarat">Gujarat (Future)</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-medium text-slate-700 block mb-1">Sector</label>
                <select
                  value={formData.sector}
                  onChange={(e) => setFormData({ ...formData, sector: e.target.value, is_food_business: e.target.value === "Food Processing" })}
                  className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                >
                  <option value="Food Processing">Food Processing</option>
                  <option value="Manufacturing">General Manufacturing</option>
                  <option value="Chemicals">Chemicals & Petrochemicals</option>
                  <option value="Textile">Textiles & Garments</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-medium text-slate-700 block mb-1">Project Stage</label>
                <select
                  value={formData.project_stage}
                  onChange={(e) => setFormData({ ...formData, project_stage: e.target.value })}
                  className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                >
                  <option value="Pre-Establishment">Pre-Establishment (Site / Blueprint)</option>
                  <option value="Pre-Operation">Pre-Operation (Commercial Launch)</option>
                  <option value="Expansion">Expansion / Unit Upgrade</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-medium text-slate-700 block mb-1">District / Cluster</label>
                <Input
                  value={formData.district}
                  onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                  placeholder="e.g. Ghaziabad, Lucknow"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-700 block mb-1">Capital Investment (₹)</label>
                <Input
                  type="number"
                  value={formData.investment}
                  onChange={(e) => setFormData({ ...formData, investment: Number(e.target.value) })}
                  placeholder="50000000"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-700 block mb-1">Workforce (Employees)</label>
                <Input
                  type="number"
                  value={formData.employees}
                  onChange={(e) => setFormData({ ...formData, employees: Number(e.target.value) })}
                  placeholder="80"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-700 block mb-1">Connected Power Load (kW)</label>
                <Input
                  type="number"
                  value={formData.connected_load_kw}
                  onChange={(e) => setFormData({ ...formData, connected_load_kw: Number(e.target.value) })}
                  placeholder="150"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-700 block mb-1">Covered Area (sqm)</label>
                <Input
                  type="number"
                  value={formData.built_up_area_sqm}
                  onChange={(e) => setFormData({ ...formData, built_up_area_sqm: Number(e.target.value) })}
                  placeholder="1200"
                />
              </div>
            </div>

            {/* Checkboxes */}
            <div className="flex flex-wrap items-center gap-6 pt-2 border-t border-slate-100">
              <label className="flex items-center gap-2 text-xs font-medium text-slate-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.has_boiler}
                  onChange={(e) => setFormData({ ...formData, has_boiler: e.target.checked })}
                  className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                />
                Operates Industrial Steam Boiler
              </label>

              <label className="flex items-center gap-2 text-xs font-medium text-slate-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.hazardous_materials}
                  onChange={(e) => setFormData({ ...formData, hazardous_materials: e.target.checked })}
                  className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                />
                Handles Hazardous / Chemical Substances
              </label>

              <label className="flex items-center gap-2 text-xs font-medium text-slate-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.is_food_business}
                  onChange={(e) => setFormData({ ...formData, is_food_business: e.target.checked })}
                  className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                />
                Direct Food Contact / FSSAI Mandate
              </label>
            </div>

            <div className="pt-2 flex justify-end">
              <Button type="submit" isLoading={isLoading} className="flex items-center gap-2 px-6">
                <Sparkles className="h-4 w-4" />
                <span>Run Intelligent Compliance Scan</span>
              </Button>
            </div>
          </form>
        </Card>

        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {isLoading && <LoadingState message="Executing Rule Engine evaluation, ML delay modeling, and RAG statutory grounding..." />}

        {/* Live Analysis Output */}
        {analysis && !isLoading && (
          <div className="space-y-6">
            {/* Top Metrics Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <span className="text-xs text-slate-500 block">Total Clearances</span>
                <span className="text-2xl font-bold text-slate-900">{analysis.summary.total_approvals}</span>
                <span className="text-[11px] text-emerald-600 block mt-0.5">
                  {analysis.summary.potentially_applicable} Applicable
                </span>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <span className="text-xs text-slate-500 block">Mandatory Documents</span>
                <span className="text-2xl font-bold text-blue-700">{analysis.summary.documents_required}</span>
                <span className="text-[11px] text-slate-400 block mt-0.5">Aggregated Checklist</span>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <span className="text-xs text-slate-500 block">ML Risk Score</span>
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-bold text-slate-900">{analysis.risk.risk_score} / 100</span>
                  <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
                    analysis.risk.risk_level === "HIGH" ? "bg-red-100 text-red-700" :
                    analysis.risk.risk_level === "MEDIUM" ? "bg-amber-100 text-amber-700" :
                    "bg-emerald-100 text-emerald-700"
                  }`}>
                    {analysis.risk.risk_level}
                  </span>
                </div>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <span className="text-xs text-slate-500 block">Predicted Processing Days</span>
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-bold text-slate-900">{Math.round(analysis.delay_prediction.predicted_days)} Days</span>
                  <span className="text-[11px] text-slate-500">P(Delay): {Math.round(analysis.delay_prediction.probability * 100)}%</span>
                </div>
              </div>
            </div>

            {/* Applicable Approvals & Clearances */}
            <Card title="Applicable Statutory Clearances" subtitle="Determined deterministically by Rule Engine based on industry parameters">
              <div className="space-y-3">
                {(analysis.approvals || []).map((appr) => (
                  <div key={appr.approval_id} className="rounded-lg border border-slate-200 bg-slate-50/50 p-4 space-y-2">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-slate-900 text-sm">{appr.approval_name}</span>
                          <span className="rounded bg-blue-100 px-2 py-0.5 text-[10px] font-mono text-blue-800">
                            {appr.approval_id}
                          </span>
                          <span className="rounded bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-700 border border-emerald-200">
                            {appr.status}
                          </span>
                        </div>
                        <p className="text-xs text-slate-500 mt-0.5">
                          Authority: <strong className="text-slate-700">{appr.authority}</strong> • SLA Target: <strong>{appr.processing_days} Days</strong> • Statutory Fee: <strong>{formatINR(appr.statutory_fee)}</strong>
                        </p>
                      </div>
                    </div>

                    <p className="text-xs text-slate-600 bg-white p-2.5 rounded border border-slate-100">
                      <strong>Rule Engine Match:</strong> {appr.reason}
                    </p>

                    {appr.documents && appr.documents.length > 0 && (
                      <div className="flex flex-wrap items-center gap-1.5 pt-1">
                        <span className="text-[11px] font-medium text-slate-500">Required Documents:</span>
                        {appr.documents.map((d, i) => (
                          <span key={i} className="inline-flex items-center gap-1 rounded bg-white px-2 py-0.5 text-xs text-slate-700 border border-slate-200">
                            <FileText className="h-3 w-3 text-slate-400" />
                            {d}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </Card>

            {/* Risk & Delay Factors */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card title="ML Delay & Bottleneck Inference" subtitle="Predictive factors from trained random forest model">
                <div className="space-y-2.5">
                  {(analysis.delay_prediction?.factors || []).map((factor, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-xs text-slate-700">
                      <Clock className="h-3.5 w-3.5 text-blue-600 shrink-0 mt-0.5" />
                      <span>{factor}</span>
                    </div>
                  ))}
                  <div className="mt-4 pt-3 border-t border-slate-100">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1.5">
                      Optimization Recommendations:
                    </span>
                    <ul className="space-y-1.5">
                      {(analysis.recommendations || []).map((rec, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-xs text-emerald-800 bg-emerald-50/70 p-2 rounded border border-emerald-100">
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0 mt-0.5" />
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </Card>

              <Card title="Statutory RAG Legal Evidence" subtitle="Retrieved and cited from official central & state acts">
                <div className="space-y-3">
                  {(analysis.regulatory_explanations || []).map((exp, idx) => (
                    <div key={idx} className="rounded-lg border border-slate-100 bg-slate-50 p-3 space-y-2 text-xs">
                      <span className="font-semibold text-slate-900 block">{exp.approval_name}</span>
                      <p className="text-slate-700 leading-relaxed">{exp.answer}</p>
                      {exp.cited_acts && exp.cited_acts.length > 0 && (
                        <div className="flex flex-wrap gap-1 pt-1">
                          {exp.cited_acts.map((act, i) => (
                            <span key={i} className="inline-flex items-center gap-1 rounded bg-white px-2 py-0.5 text-[11px] text-blue-800 border border-blue-100">
                              <BookOpen className="h-3 w-3 text-blue-500" />
                              {act}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            {/* Official Sources Citation Bar */}
            {analysis.sources && analysis.sources.length > 0 && (
              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm text-xs text-slate-600 space-y-2">
                <span className="font-semibold text-slate-800 block">Cited Statutory Authorities & Sources:</span>
                <div className="flex flex-wrap gap-2">
                  {analysis.sources.map((src, idx) => (
                    <a
                      key={idx}
                      href={src.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-slate-700 hover:bg-slate-100 transition"
                    >
                      <span>{src.source_name}</span>
                      <span className="text-[10px] text-slate-400 font-mono">({src.authority})</span>
                      <ExternalLink className="h-3 w-3 text-slate-400" />
                    </a>
                  ))}
                </div>
                <p className="text-[11px] text-slate-400 pt-2 border-t border-slate-100">
                  {analysis.disclaimer}
                </p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
