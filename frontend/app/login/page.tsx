"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { authService } from "@/services/authService";
import { DEMO_ACCOUNTS } from "@/lib/constants";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card } from "@/components/ui/Card";
import { Alert } from "@/components/ui/Alert";
import { Shield, ArrowRight, UserCheck } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("entrepreneur@abcfoods.com");
  const [password, setPassword] = useState("password123");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e?: React.FormEvent, customEmail?: string, customPassword?: string) => {
    if (e) e.preventDefault();
    setIsLoading(true);
    setError(null);

    const loginEmail = customEmail || email;
    const loginPassword = customPassword || password;

    try {
      const res = await authService.login(loginEmail, loginPassword);
      if (res.role === "government_officer" || res.role === "department_officer") {
        router.push("/government/dashboard");
      } else if (res.role === "administrator") {
        router.push("/admin");
      } else {
        router.push("/dashboard");
      }
    } catch (err: any) {
      setError(err.message || "Failed to log in. Ensure backend is running.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoSelect = (acc: typeof DEMO_ACCOUNTS[0]) => {
    setEmail(acc.email);
    setPassword(acc.password);
    handleLogin(undefined, acc.email, acc.password);
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4 bg-slate-50">
      <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
        {/* Login Form */}
        <Card className="p-8 shadow-md">
          <div className="flex items-center gap-2 mb-6">
            <div className="h-8 w-8 rounded-lg bg-blue-700 text-white flex items-center justify-center">
              <Shield className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900">Sign In to Portal</h2>
              <p className="text-xs text-slate-500">Bharat Single-Window Compliance Solution</p>
            </div>
          </div>

          {error && (
            <Alert variant="error" className="mb-4 text-xs">
              {error}
            </Alert>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <Input
              label="Email Address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <Button type="submit" className="w-full" isLoading={isLoading}>
              Sign In
            </Button>
          </form>
        </Card>

        {/* Demo Account Quick Switcher */}
        <div className="space-y-4">
          <div className="rounded-xl border border-blue-200 bg-blue-50/60 p-5">
            <div className="flex items-center gap-2 text-blue-900 font-semibold text-sm mb-2">
              <UserCheck className="h-4 w-4 text-blue-700" />
              <span>SIH Hackathon Quick Demo Access</span>
            </div>
            <p className="text-xs text-slate-600 mb-4">
              Click any role below to instantly authenticate with pre-seeded synthetic data.
            </p>

            <div className="space-y-2.5">
              {DEMO_ACCOUNTS.map((acc) => (
                <button
                  key={acc.role}
                  type="button"
                  onClick={() => handleDemoSelect(acc)}
                  disabled={isLoading}
                  className="w-full text-left rounded-lg border border-slate-200 bg-white p-3 hover:border-blue-500 hover:shadow-sm transition group flex items-center justify-between"
                >
                  <div>
                    <span className="text-xs font-semibold text-slate-900 block group-hover:text-blue-700">
                      {acc.label}
                    </span>
                    <span className="text-[11px] text-slate-500 block">{acc.email}</span>
                  </div>
                  <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-blue-700 transition" />
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
