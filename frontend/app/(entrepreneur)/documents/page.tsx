"use client";

import React, { useEffect, useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Card } from "@/components/ui/Card";
import { DocumentCard } from "@/components/domain/DocumentCard";
import { UploadDocumentModal } from "@/components/domain/UploadDocumentModal";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { LoadingState } from "@/components/ui/LoadingState";
import { applicationService } from "@/services/applicationService";
import { aiService } from "@/services/aiService";
import { DocumentItem, DocumentValidationResponse } from "@/types";
import {
  Upload,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  FileText,
  Sparkles,
  Lock,
  Eye,
  Info
} from "lucide-react";

export default function DocumentsPage() {
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  // Document AI Interactive Pre-Validation Form State
  const [showValidator, setShowValidator] = useState(false);
  const [docType, setDocType] = useState("Fire Safety NOC");
  const [expectedEntity, setExpectedEntity] = useState("Pragati Foods Pvt Ltd");
  const [sampleText, setSampleText] = useState(
    `GOVERNMENT OF UTTAR PRADESH\nUTTAR PRADESH FIRE SERVICE HEADQUARTERS, LUCKNOW\n\nPROVISIONAL FIRE SAFETY NO OBJECTION CERTIFICATE\nCertificate Number: UP-FIRE-NOC-2026-88421\nIssue Date: 2026-01-15\nExpiry Date: 2029-01-14\n\nEnterprise Name: Pragati Foods Private Limited\nAuthority: Office of Chief Fire Officer, Lucknow\n\nApplicant PAN: AAACB1234F\nAadhaar of Nominated Occupier: 4582 9182 3019\nBank Account Reference: 98124500129381`
  );
  const [valResult, setValResult] = useState<DocumentValidationResponse | null>(null);
  const [isValLoading, setIsValLoading] = useState(false);

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

  const handleRunValidation = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsValLoading(true);

    try {
      const res = await aiService.validateDocument({
        document_id: "DOC_PREVAL_" + Date.now().toString().slice(-4),
        filename: `${docType.toLowerCase().replace(/\s+/g, "_")}.txt`,
        document_type: docType,
        file_content_text: sampleText,
        expected_entity_name: expectedEntity,
        expected_document_type: docType,
      });
      setValResult(res);
    } catch (err: any) {
      console.error("Document validation error", err);
    } finally {
      setIsValLoading(false);
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)] bg-slate-50">
      <Sidebar role="entrepreneur" />
      <main className="flex-1 p-6 sm:p-8 space-y-6 max-w-5xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-slate-900">Document Vault & AI Pre-Validation</h1>
            <p className="text-xs text-slate-500">
              Reusable enterprise credentials and 100% local privacy-safe pre-validation
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              size="sm"
              onClick={() => setIsUploadModalOpen(true)}
              className="flex items-center gap-1.5"
            >
              <Upload className="h-3.5 w-3.5" />
              Upload Document
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowValidator(!showValidator)}
              className="flex items-center gap-1.5"
            >
              <Sparkles className="h-3.5 w-3.5" />
              {showValidator ? "Hide Pre-Validator" : "Test Document AI Pre-Validation"}
            </Button>
          </div>
        </div>

        {/* Interactive Document AI Pre-Validation Panel */}
        {showValidator && (
          <Card
            title="Document AI Pre-Validation Studio"
            subtitle="Test local readability, corporate entity name matching, expiry verification, and PII masking"
          >
            <form onSubmit={handleRunValidation} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-slate-700 block mb-1">Expected Document Type</label>
                  <select
                    value={docType}
                    onChange={(e) => setDocType(e.target.value)}
                    className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                  >
                    <option value="Fire Safety NOC">Fire Safety NOC</option>
                    <option value="FSSAI Food License">FSSAI Food License</option>
                    <option value="Factory License">Factory License</option>
                    <option value="Site Plan">Site Plan / Blueprint</option>
                    <option value="Potable Water Test Report">Potable Water Test Report</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-medium text-slate-700 block mb-1">Expected Enterprise Name</label>
                  <Input
                    value={expectedEntity}
                    onChange={(e) => setExpectedEntity(e.target.value)}
                    placeholder="e.g. Pragati Foods Pvt Ltd"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-xs font-medium text-slate-700">Document Text Payload (Local Processing Only)</label>
                  <span className="text-[11px] text-emerald-700 flex items-center gap-1">
                    <Lock className="h-3 w-3" /> PII Masked in Logs
                  </span>
                </div>
                <textarea
                  rows={6}
                  value={sampleText}
                  onChange={(e) => setSampleText(e.target.value)}
                  className="w-full rounded-md border border-slate-300 bg-slate-50 p-3 text-xs font-mono text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
              </div>

              <div className="flex justify-end">
                <Button type="submit" isLoading={isValLoading} size="sm" className="flex items-center gap-1.5">
                  <ShieldCheck className="h-4 w-4" /> Run Pre-Validation Check
                </Button>
              </div>
            </form>

            {/* Validation Result Box */}
            {valResult && (
              <div className="mt-4 pt-4 border-t border-slate-200 space-y-3 text-xs">
                <div className="flex flex-wrap items-center justify-between gap-2 bg-slate-50 p-3 rounded-lg border border-slate-200">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-slate-900">Pre-Validation Status:</span>
                    <span
                      className={`font-semibold px-2 py-0.5 rounded text-xs ${
                        valResult.status === "VALID"
                          ? "bg-emerald-100 text-emerald-700"
                          : valResult.status === "WARNING"
                          ? "bg-amber-100 text-amber-700"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      {valResult.status}
                    </span>
                  </div>
                  <div className="text-slate-500">
                    Confidence: <strong>{Math.round(valResult.confidence * 100)}%</strong> • Entity Match: <strong>{valResult.entity_match}</strong> • Validity: <strong>{valResult.expiry_status}</strong>
                  </div>
                </div>

                {/* Sub-Checks Checklist */}
                {valResult.checks && valResult.checks.length > 0 && (
                  <div className="space-y-1.5">
                    <span className="font-semibold text-slate-700 block">Inspection Sub-Checks:</span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {valResult.checks.map((chk, i) => (
                        <div
                          key={i}
                          className="flex items-start gap-2 bg-white p-2.5 rounded border border-slate-200 text-[11px]"
                        >
                          {chk.passed ? (
                            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0 mt-0.5" />
                          ) : (
                            <AlertTriangle className="h-3.5 w-3.5 text-amber-500 shrink-0 mt-0.5" />
                          )}
                          <div>
                            <strong className="text-slate-800">{chk.check_name}:</strong>{" "}
                            <span className="text-slate-600">{chk.details}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Warnings / Errors */}
                {valResult.warnings && valResult.warnings.length > 0 && (
                  <div className="rounded-lg bg-amber-50 p-3 text-amber-800 space-y-1">
                    <span className="font-semibold block text-[11px]">Advisory Warnings:</span>
                    {valResult.warnings.map((w, i) => (
                      <p key={i}>• {w}</p>
                    ))}
                  </div>
                )}

                {valResult.errors && valResult.errors.length > 0 && (
                  <div className="rounded-lg bg-red-50 p-3 text-red-800 space-y-1">
                    <span className="font-semibold block text-[11px]">Validation Discrepancies:</span>
                    {valResult.errors.map((e, i) => (
                      <p key={i}>• {e}</p>
                    ))}
                  </div>
                )}

                {/* Redacted Preview */}
                {valResult.redacted_preview && (
                  <div className="rounded-lg bg-slate-900 text-slate-300 p-3 font-mono text-[10px] space-y-1">
                    <span className="text-slate-400 block font-semibold">PII-Sanitized Audit Representation:</span>
                    <pre className="whitespace-pre-wrap">{valResult.redacted_preview}...</pre>
                  </div>
                )}

                <p className="text-[10px] text-slate-400 italic">
                  {valResult.disclaimer}
                </p>
              </div>
            )}
          </Card>
        )}

        {/* Existing Vault List */}
        {isLoading ? (
          <LoadingState message="Loading document repository..." />
        ) : (
          <div className="space-y-3">
            {docs.map((doc) => (
              <DocumentCard key={doc.id} doc={doc} />
            ))}
          </div>
        )}

        {/* Upload Document Modal */}
        <UploadDocumentModal
          isOpen={isUploadModalOpen}
          onClose={() => setIsUploadModalOpen(false)}
          onSuccess={(newDoc) => {
            setDocs((prev) => [newDoc, ...prev]);
          }}
          businessId="biz-001"
          applicationId="app-001"
        />
      </main>
    </div>
  );
}
