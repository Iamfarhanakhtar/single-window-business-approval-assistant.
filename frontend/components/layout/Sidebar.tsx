"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Building2,
  CheckSquare,
  FolderKanban,
  FileText,
  RefreshCw,
  Gift,
  Bot,
  BarChart3,
  CalendarCheck,
  Clock,
  Users,
  ShieldAlert,
  BookOpen
} from "lucide-react";

export interface SidebarProps {
  role?: "entrepreneur" | "government" | "admin";
}

export const Sidebar: React.FC<SidebarProps> = ({ role = "entrepreneur" }) => {
  const pathname = usePathname();

  const entrepreneurLinks = [
    { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
    { href: "/business", label: "Business Profile", icon: Building2 },
    { href: "/approvals", label: "Approval Roadmap", icon: CheckSquare },
    { href: "/applications", label: "My Applications", icon: FolderKanban },
    { href: "/documents", label: "Document Vault", icon: FileText },
    { href: "/renewals", label: "Renewals & Validity", icon: RefreshCw },
    { href: "/incentives", label: "Eligible Incentives", icon: Gift },
    { href: "/assistant", label: "AI Regulatory Assistant", icon: Bot },
  ];

  const governmentLinks = [
    { href: "/government/dashboard", label: "Executive Dashboard", icon: LayoutDashboard },
    { href: "/government/applications", label: "Scrutiny Queue", icon: FolderKanban },
    { href: "/government/inspections", label: "Site Inspections", icon: CalendarCheck },
    { href: "/government/sla", label: "SLA & Bottlenecks", icon: Clock },
    { href: "/government/analytics", label: "State Analytics", icon: BarChart3 },
  ];

  const adminLinks = [
    { href: "/admin", label: "Admin Console", icon: LayoutDashboard },
    { href: "/admin/users", label: "User Management", icon: Users },
    { href: "/admin/regulations", label: "Acts & Rules KB", icon: BookOpen },
    { href: "/admin/departments", label: "Department Config", icon: Building2 },
  ];

  const links =
    role === "government" ? governmentLinks : role === "admin" ? adminLinks : entrepreneurLinks;

  return (
    <aside className="w-64 shrink-0 border-r border-slate-200 bg-white min-h-[calc(100vh-4rem)] flex flex-col justify-between p-4">
      <div className="space-y-6">
        <div>
          <span className="px-3 text-[11px] font-bold uppercase tracking-wider text-slate-400">
            {role.toUpperCase()} PORTAL
          </span>
          <nav className="mt-2 space-y-1">
            {links.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href || (link.href !== "/dashboard" && pathname.startsWith(link.href));

              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition",
                    isActive
                      ? "bg-blue-50 text-blue-700 font-semibold shadow-xs"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                  )}
                >
                  <Icon className={cn("h-4 w-4", isActive ? "text-blue-700" : "text-slate-400")} />
                  {link.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      <div className="rounded-xl border border-blue-100 bg-blue-50/50 p-3.5 text-xs text-slate-600">
        <span className="font-semibold text-blue-900 block mb-1">Business Compliance Hub</span>
        <p className="text-[11px] leading-relaxed text-slate-500">
          Unified Intelligent Single-Window Clearance & Compliance Automation.
        </p>
      </div>
    </aside>
  );
};
