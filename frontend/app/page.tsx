import React from "react";
import Link from "next/link";
import {
  ShieldCheck,
  Zap,
  Network,
  CalendarCheck2,
  Clock,
  Bot,
  ArrowRight,
  Building2,
  CheckCircle2,
  Lock,
  Layers
} from "lucide-react";
import { Button } from "@/components/ui/Button";

export default function LandingPage() {
  const capabilities = [
    {
      icon: Network,
      title: "Parallel Departmental Clearances",
      desc: "Run Fire NOC, Pollution CTE, Factory Clearances, and Labour Approvals in parallel with automated cross-department state sync."
    },
    {
      icon: Zap,
      title: "Customized Checklist Generator",
      desc: "Deterministic rule engine coupled with RAG produces tailored compliance roadmaps based on sector, capital investment, and location."
    },
    {
      icon: ShieldCheck,
      title: "Document Vault & Pre-Validation",
      desc: "Reuse verified enterprise credentials and pre-validate structural schematics & certificates prior to formal submission."
    },
    {
      icon: Clock,
      title: "Predictive SLA & Delay Forecasting",
      desc: "ML inference models forecast inter-department bottlenecks, query probability, and compute expected processing duration."
    },
    {
      icon: CalendarCheck2,
      title: "Unified Inspection Dispatcher",
      desc: "Consolidate multi-agency site visits into synchronized joint inspections with geo-tagged verification reports."
    },
    {
      icon: Bot,
      title: "AI Regulatory Intelligence",
      desc: "Statutory RAG assistant providing precise citations from central and state industrial acts, eliminating procedural ambiguity."
    }
  ];

  return (
    <div className="flex flex-col min-h-[calc(100vh-4rem)]">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-slate-900 py-20 text-white sm:py-28">
        <div className="absolute inset-0 bg-[radial-gradient(#1e3a8a_1px,transparent_1px)] [background-size:20px_20px] opacity-20" />
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-900/40 px-3.5 py-1 text-xs font-semibold text-blue-300 backdrop-blur-sm mb-6">
            <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            Smart India Hackathon • Problem Statement 130
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-6xl text-white max-w-4xl mx-auto leading-tight">
            Unified Intelligent Approval & Compliance Management
          </h1>
          <p className="mt-6 text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
            A single-window Gov-Tech platform designed for industrial units and entrepreneurs.
            Parallel departmental workflows, AI-assisted document pre-validation, and predictive SLA tracking.
          </p>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link href="/dashboard">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-500 text-white font-semibold flex items-center gap-2 px-8">
                Launch Entrepreneur Portal
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/government/dashboard">
              <Button size="lg" variant="outline" className="border-slate-700 bg-slate-800 text-slate-200 hover:bg-slate-700">
                Government Officer Portal
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="ghost" className="text-slate-300 hover:bg-slate-800">
                Demo Accounts
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Demonstration Highlight Bar */}
      <section className="border-y border-slate-200 bg-white py-4 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl flex flex-wrap items-center justify-between gap-4 text-xs font-medium text-slate-600">
          <div className="flex items-center gap-2">
            <Building2 className="h-4 w-4 text-blue-700" />
            <span>Demonstration Entity: <strong className="text-slate-900">ABC Foods Pvt Ltd</strong> (Food Processing • Ghaziabad, UP • ₹5 Cr)</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5 text-emerald-700">
              <CheckCircle2 className="h-3.5 w-3.5" /> 4 Approvals in Parallel
            </span>
            <span className="flex items-center gap-1.5 text-blue-700">
              <Layers className="h-3.5 w-3.5" /> 17 Database Models
            </span>
            <span className="flex items-center gap-1.5 text-slate-700">
              <Lock className="h-3.5 w-3.5" /> RBAC Enabled
            </span>
          </div>
        </div>
      </section>

      {/* Core Architectural Capabilities */}
      <section className="py-16 bg-slate-50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto">
            <h2 className="text-xs font-bold uppercase tracking-wider text-blue-700">System Architecture</h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
              Engineered for Speed, Transparency & Compliance
            </p>
          </div>

          <div className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {capabilities.map((cap, idx) => {
              const Icon = cap.icon;
              return (
                <div key={idx} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm hover:border-blue-200 transition">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-700 mb-4">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="text-base font-semibold text-slate-900">{cap.title}</h3>
                  <p className="mt-2 text-xs text-slate-500 leading-relaxed">{cap.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>
    </div>
  );
}
