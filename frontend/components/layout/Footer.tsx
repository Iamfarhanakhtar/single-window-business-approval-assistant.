import React from "react";

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
      <div className="mx-auto max-w-7xl px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
        <p>© 2026 Bharat Single-Window Compliance Intelligence Solution • Smart India Hackathon PS-130</p>
        <p className="text-slate-400">Strictly for demonstration with synthetic data</p>
      </div>
    </footer>
  );
};
