"use client";

import React from "react";
import Link from "next/link";
import { authService } from "@/services/authService";
import { Shield, Bell, User, LogOut, ExternalLink } from "lucide-react";
import { Button } from "../ui/Button";

export const Navbar: React.FC = () => {
  const user = typeof window !== "undefined" ? authService.getStoredUser() : null;

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/95 backdrop-blur-sm">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-700 text-white shadow-sm">
              <Shield className="h-5 w-5" />
            </div>
            <div>
              <span className="text-base font-bold tracking-tight text-slate-900 block leading-tight">
                Bharat Compliance
              </span>
              <span className="text-[10px] font-semibold text-blue-700 tracking-wider uppercase block">
                Single-Window Approval Intelligence
              </span>
            </div>
          </Link>
        </div>

        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-4">
              <div className="hidden md:flex flex-col text-right">
                <span className="text-xs font-semibold text-slate-900">{user.full_name}</span>
                <span className="text-[10px] font-medium text-slate-500 uppercase tracking-wider">
                  {user.role.replace(/_/g, " ")}
                </span>
              </div>
              <button
                onClick={() => authService.logout()}
                className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 transition"
              >
                <LogOut className="h-3.5 w-3.5 text-slate-500" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link href="/login">
                <Button variant="outline" size="sm">Log In</Button>
              </Link>
              <Link href="/login">
                <Button size="sm">Get Started</Button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
