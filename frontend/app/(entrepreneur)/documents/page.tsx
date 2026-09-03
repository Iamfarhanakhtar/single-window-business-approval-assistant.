"use client";

import React, { useEffect, useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Card } from "@/components/ui/Card";
import { DocumentCard } from "@/components/domain/DocumentCard";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/LoadingState";
import { applicationService } from "@/services/applicationService";
import { DocumentItem } from "@/types";
import { Upload } from "lucide-react";

export default function DocumentsPage() {
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const list = await applicationService.getDocuments();
        setDocs(list);
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
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-900">Document Vault & Verification</h1>
            <p className="text-xs text-slate-500">Reusable enterprise credentials and AI pre-validated blueprints</p>
          </div>
          <Button size="sm" className="flex items-center gap-1.5">
            <Upload className="h-3.5 w-3.5" /> Upload New File
          </Button>
        </div>

        {isLoading ? (
          <LoadingState message="Loading document repository..." />
        ) : (
          <div className="space-y-3">
            {docs.map((doc) => (
              <DocumentCard key={doc.id} doc={doc} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
