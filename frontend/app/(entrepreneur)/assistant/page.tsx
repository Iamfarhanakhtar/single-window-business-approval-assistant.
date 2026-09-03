"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { aiService } from "@/services/aiService";
import { Bot, Send, BookOpen, ShieldCheck, Sparkles } from "lucide-react";

export default function AssistantPage() {
  const [question, setQuestion] = useState("");
  const [conversation, setConversation] = useState<Array<{ q: string; a: string; acts?: string[] }>>([
    {
      q: "What are the deemed approval rules for UPPCB Consent to Establish in Uttar Pradesh?",
      a: "Under the Uttar Pradesh Single Window Clearance Act and Water Act 1974 Section 25, if no query or inspection objection is formally raised within 30 days of submission, the applicant is entitled to deemed CTE clearance.",
      acts: ["UP Single Window Act 2018", "Water (Prevention & Control of Pollution) Act 1974 Sec 25"]
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    const userQ = question;
    setQuestion("");
    setIsLoading(true);

    try {
      const res = await aiService.askRegulatoryRAG(userQ, "Food Processing", "Uttar Pradesh");
      setConversation((prev) => [...prev, { q: userQ, a: res.answer, acts: res.cited_acts }]);
    } catch (err: any) {
      setConversation((prev) => [
        ...prev,
        { q: userQ, a: "Could not retrieve legal response: " + err.message }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)] bg-slate-50">
      <Sidebar role="entrepreneur" />
      <main className="flex-1 p-6 sm:p-8 space-y-6 max-w-4xl">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-700" />
            <h1 className="text-xl font-bold text-slate-900">AI Regulatory Intelligence Assistant</h1>
          </div>
          <p className="text-xs text-slate-500">
            Ask questions about statutory compliance, required documents, state schemes, and acts.
          </p>
        </div>

        <div className="space-y-4">
          {conversation.map((item, idx) => (
            <div key={idx} className="space-y-3">
              {/* User Message */}
              <div className="flex justify-end">
                <div className="max-w-lg rounded-xl bg-blue-700 p-3.5 text-sm text-white shadow-sm">
                  {item.q}
                </div>
              </div>

              {/* Bot Response */}
              <div className="flex gap-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-100 text-blue-700">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="max-w-xl rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-800 shadow-sm space-y-3">
                  <p className="leading-relaxed">{item.a}</p>
                  {item.acts && item.acts.length > 0 && (
                    <div className="pt-2 border-t border-slate-100">
                      <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                        Cited Statutory Acts & Clauses:
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {item.acts.map((act, i) => (
                          <span key={i} className="inline-flex items-center gap-1 rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-700">
                            <BookOpen className="h-3 w-3 text-slate-400" />
                            {act}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3 text-xs text-slate-400 items-center">
              <Bot className="h-4 w-4 animate-spin text-blue-600" />
              <span>Analyzing central and state regulatory knowledge base...</span>
            </div>
          )}
        </div>

        <form onSubmit={handleAsk} className="sticky bottom-6 flex gap-2">
          <Input
            placeholder="Ask about fire NOC mandates, pollution limits, subsidy schemes..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={isLoading}
            className="shadow-md"
          />
          <Button type="submit" isLoading={isLoading} className="shrink-0 flex items-center gap-1.5">
            <Send className="h-4 w-4" />
            <span>Send</span>
          </Button>
        </form>
      </main>
    </div>
  );
}
